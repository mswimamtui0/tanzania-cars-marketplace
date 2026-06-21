# Add these to existing communication/views.py

from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Escalation, EscalationComment, YardManagerAssignment
from django.contrib.auth.models import User

# Helper function to check if user is yard manager
def is_yard_manager(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'yard_manager'

def is_admin(user):
    return user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role == 'admin')

# 1. BUYER ESCALATES TO YARD MANAGER (if dealer unresponsive)
@login_required
def escalate_to_yard_manager(request, dealer_id, car_id=None):
    """Buyer escalates when dealer doesn't respond"""
    dealer = get_object_or_404(User, id=dealer_id)
    car = get_object_or_404(CarListing, id=car_id) if car_id else None
    
    # Find which yard manager is assigned to this dealer
    yard_assignment = YardManagerAssignment.objects.filter(dealer=dealer, is_active=True).first()
    
    if not yard_assignment:
        messages.error(request, 'No yard manager assigned to this dealer yet. Your escalation will go directly to admin.')
        return redirect('escalate_to_admin', dealer_id=dealer_id, car_id=car_id)
    
    yard_manager = yard_assignment.yard_manager
    
    if request.method == 'POST':
        # Check if dealer was actually unresponsive
        last_conversation = Conversation.objects.filter(participants=dealer).filter(participants=request.user).first()
        
        if last_conversation:
            last_message = last_conversation.messages.filter(sender=dealer).order_by('-created_at').first()
            if last_message and last_message.created_at > timezone.now() - timedelta(hours=48):
                messages.error(request, 'Dealer has responded within 48 hours. Please wait for their response.')
                return redirect('conversation_detail', conversation_id=last_conversation.id)
        
        # Create escalation
        escalation = Escalation.objects.create(
            buyer=request.user,
            dealer=dealer,
            yard_manager=yard_manager,
            car=car,
            reason=request.POST.get('reason'),
            description=request.POST.get('description'),
            evidence=request.FILES.get('evidence'),
            current_level='level_2',
            status='escalated_yard',
            escalated_to_yard_at=timezone.now()
        )
        
        # Notify yard manager
        send_mail(
            subject=f'🚨 ESCALATION #{escalation.id}: Buyer vs {dealer.username}',
            message=f"""
            Buyer: {request.user.username}
            Dealer: {dealer.username}
            Reason: {request.POST.get('reason')}
            Description: {request.POST.get('description')}
            
            Please login to your dashboard to investigate and resolve.
            URL: https://tanzaniacarmarket.com/communication/escalation/{escalation.id}/
            """,
            from_email='noreply@tanzaniacarmarket.com',
            recipient_list=[yard_manager.email],
            fail_silently=False,
        )
        
        messages.success(request, f'Escalation #{escalation.id} submitted! The yard manager will investigate within 24 hours.')
        return redirect('my_escalations')
    
    return render(request, 'communication/escalate_to_yard.html', {
        'dealer': dealer,
        'car': car,
        'yard_manager': yard_manager
    })

# 2. YARD MANAGER VIEWS & RESOLVES ESCALATIONS
@login_required
@user_passes_test(is_yard_manager)
def yard_manager_escalations(request):
    """Yard manager sees all escalations assigned to them"""
    escalations = Escalation.objects.filter(
        yard_manager=request.user
    ).exclude(status='resolved').order_by('-created_at')
    
    resolved = Escalation.objects.filter(
        yard_manager=request.user,
        status='resolved'
    ).order_by('-resolved_at')[:20]
    
    context = {
        'pending_escalations': escalations.filter(status__in=['escalated_yard', 'yard_investigating']),
        'under_review': escalations.filter(status='yard_investigating'),
        'resolved_escalations': resolved,
        'total_count': escalations.count(),
    }
    return render(request, 'communication/yard_escalations.html', context)

@login_required
@user_passes_test(is_yard_manager)
def yard_resolve_escalation(request, escalation_id):
    """Yard manager resolves escalation"""
    escalation = get_object_or_404(Escalation, id=escalation_id, yard_manager=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'contact_dealer':
            # Send warning to dealer
            send_mail(
                subject=f' Escalation #{escalation.id} - Action Required',
                message=f"""
                Dear {escalation.dealer.username},
                
                A buyer has escalated an issue regarding your unresponsiveness.
                
                Issue: {escalation.description}
                
                Please respond to the buyer within 24 hours.
                
                If no response, further action will be taken.
                
                Regards,
                Yard Manager: {request.user.username}
                """,
                from_email='noreply@tanzaniacarmarket.com',
                recipient_list=[escalation.dealer.email],
                fail_silently=False,
            )
            
            escalation.status = 'yard_investigating'
            escalation.save()
            
            EscalationComment.objects.create(
                escalation=escalation,
                author=request.user,
                comment=f"Dealer contacted via email. Waiting for response.",
                is_internal=False
            )
            
            messages.success(request, 'Dealer has been contacted and warned.')
            
        elif action == 'escalate_admin':
            # Yard manager escalates to admin
            escalation.current_level = 'level_3'
            escalation.status = 'escalated_admin'
            escalation.escalated_to_admin_at = timezone.now()
            escalation.save()
            
            # Notify admin
            admins = User.objects.filter(is_superuser=True)
            for admin in admins:
                send_mail(
                    subject=f'🚨 URGENT: Escalation #{escalation.id} escalated to Admin',
                    message=f"""
                    Yard Manager {request.user.username} has escalated this case.
                    
                    Buyer: {escalation.buyer.username}
                    Dealer: {escalation.dealer.username}
                    Reason: {escalation.reason}
                    
                    Please review and take action.
                    """,
                    from_email='noreply@tanzaniacarmarket.com',
                    recipient_list=[admin.email],
                    fail_silently=False,
                )
            
            messages.warning(request, 'Case escalated to Admin for final resolution.')
            
        elif action == 'resolve':
            escalation.status = 'resolved'
            escalation.resolved_at = timezone.now()
            escalation.resolution_notes = request.POST.get('resolution_notes', '')
            escalation.resolution_type = request.POST.get('resolution_type')
            escalation.save()
            
            # Notify buyer
            send_mail(
                subject=f' Escalation #{escalation.id} Resolved',
                message=f"""
                Dear {escalation.buyer.username},
                
                Your escalation has been resolved.
                
                Resolution: {escalation.resolution_notes}
                
                Thank you for your patience.
                
                Regards,
                {request.user.username} (Yard Manager)
                """,
                from_email='noreply@tanzaniacarmarket.com',
                recipient_list=[escalation.buyer.email],
                fail_silently=False,
            )
            
            messages.success(request, 'Escalation resolved and buyer notified.')
        
        elif action == 'compensate':
            escalation.resolution_type = 'compensation'
            escalation.compensation_amount = request.POST.get('compensation_amount')
            escalation.resolution_notes = request.POST.get('resolution_notes')
            escalation.status = 'resolved'
            escalation.resolved_at = timezone.now()
            escalation.save()
            
            messages.success(request, f'Compensation of TSh {escalation.compensation_amount} approved.')
        
        return redirect('yard_manager_escalations')
    
    return render(request, 'communication/yard_resolve_escalation.html', {'escalation': escalation})

# 3. ADMIN VIEWS ALL USERS & ESCALATIONS
@login_required
@user_passes_test(is_admin)
def admin_all_users(request):
    """Admin can view and manage all users"""
    users = User.objects.all().select_related('userprofile')
    
    # Filter by role
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(userprofile__role=role_filter)
    
    # Search
    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            Q(username__icontains=search) | 
            Q(email__icontains=search) |
            Q(userprofile__phone__icontains=search)
        )
    
    context = {
        'users': users,
        'total_users': users.count(),
        'admins': User.objects.filter(userprofile__role='admin').count(),
        'dealers': User.objects.filter(userprofile__role='dealer').count(),
        'yard_managers': User.objects.filter(userprofile__role='yard_manager').count(),
        'buyers': User.objects.filter(userprofile__role='buyer').count(),
    }
    return render(request, 'communication/admin_all_users.html', context)

@login_required
@user_passes_test(is_admin)
def admin_manage_user(request, user_id):
    """Admin can edit/delete/suspend any user"""
    target_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'suspend':
            target_user.is_active = False
            target_user.save()
            messages.success(request, f'User {target_user.username} suspended.')
            
            # Notify user
            send_mail(
                subject='Account Suspended',
                message='Your account has been suspended. Contact admin for more information.',
                from_email='noreply@tanzaniacarmarket.com',
                recipient_list=[target_user.email],
                fail_silently=False,
            )
            
        elif action == 'activate':
            target_user.is_active = True
            target_user.save()
            messages.success(request, f'User {target_user.username} activated.')
            
        elif action == 'change_role':
            new_role = request.POST.get('new_role')
            target_user.userprofile.role = new_role
            target_user.userprofile.save()
            messages.success(request, f'User role changed to {new_role}')
            
        elif action == 'delete':
            target_user.delete()
            messages.warning(request, f'User {target_user.username} deleted.')
            return redirect('admin_all_users')
        
        elif action == 'assign_yard_manager':
            yard_manager_id = request.POST.get('yard_manager_id')
            yard_manager = get_object_or_404(User, id=yard_manager_id)
            
            YardManagerAssignment.objects.update_or_create(
                dealer=target_user,
                defaults={'yard_manager': yard_manager, 'is_active': True}
            )
            messages.success(request, f'Yard Manager {yard_manager.username} assigned to dealer {target_user.username}')
    
    yard_managers = User.objects.filter(userprofile__role='yard_manager')
    current_assignment = YardManagerAssignment.objects.filter(dealer=target_user, is_active=True).first()
    
    return render(request, 'communication/admin_manage_user.html', {
        'target_user': target_user,
        'yard_managers': yard_managers,
        'current_assignment': current_assignment,
    })

@login_required
@user_passes_test(is_admin)
def admin_all_escalations(request):
    """Admin views all escalations in system"""
    escalations = Escalation.objects.all().order_by('-created_at')
    
    # Filters
    status_filter = request.GET.get('status', '')
    if status_filter:
        escalations = escalations.filter(status=status_filter)
    
    level_filter = request.GET.get('level', '')
    if level_filter:
        escalations = escalations.filter(current_level=level_filter)
    
    context = {
        'escalations': escalations,
        'total': escalations.count(),
        'pending_yard': escalations.filter(current_level='level_2', status__in=['escalated_yard', 'yard_investigating']).count(),
        'pending_admin': escalations.filter(current_level='level_3', status='escalated_admin').count(),
        'resolved': escalations.filter(status='resolved').count(),
    }
    return render(request, 'communication/admin_all_escalations.html', context)

@login_required
@user_passes_test(is_admin)
def admin_resolve_escalation(request, escalation_id):
    """Admin final resolution"""
    escalation = get_object_or_404(Escalation, id=escalation_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'suspend_dealer':
            escalation.dealer.is_active = False
            escalation.dealer.save()
            escalation.action_taken_against_dealer = 'Dealer suspended'
            
        elif action == 'remove_dealer':
            escalation.dealer.delete()
            escalation.action_taken_against_dealer = 'Dealer removed from platform'
            
        elif action == 'warning':
            escalation.action_taken_against_dealer = 'Official warning issued'
            # Send warning email
            send_mail(
                subject='Final Warning from Admin',
                message=f'You have received an official warning due to escalation #{escalation.id}. Future violations may result in suspension.',
                from_email='noreply@tanzaniacarmarket.com',
                recipient_list=[escalation.dealer.email],
                fail_silently=False,
            )
        
        escalation.status = 'resolved'
        escalation.resolution_type = request.POST.get('resolution_type')
        escalation.resolution_notes = request.POST.get('resolution_notes')
        escalation.admin = request.user
        escalation.resolved_at = timezone.now()
        escalation.save()
        
        # Notify all parties
        for recipient in [escalation.buyer.email, escalation.dealer.email]:
            if escalation.yard_manager:
                recipient.append(escalation.yard_manager.email)
        
        send_mail(
            subject=f'Final Resolution: Escalation #{escalation.id}',
            message=f"""
            Dear Parties,
            
            Escalation #{escalation.id} has been resolved by Admin.
            
            Resolution: {escalation.resolution_notes}
            Action Taken: {escalation.action_taken_against_dealer or 'None'}
            
            This case is now closed.
            
            Regards,
            Administrator
            """,
            from_email='noreply@tanzaniacarmarket.com',
            recipient_list=[escalation.buyer.email, escalation.dealer.email],
            fail_silently=False,
        )
        
        messages.success(request, 'Escalation resolved and all parties notified.')
        return redirect('admin_all_escalations')
    
    return render(request, 'communication/admin_resolve_escalation.html', {'escalation': escalation})

# 4. BUYER VIEWS THEIR ESCALATIONS
@login_required
def my_escalations(request):
    """Buyer sees all their escalations"""
    escalations = Escalation.objects.filter(buyer=request.user).order_by('-created_at')
    return render(request, 'communication/my_escalations.html', {'escalations': escalations})

@login_required
def escalation_detail(request, escalation_id):
    """View single escalation details"""
    escalation = get_object_or_404(Escalation, id=escalation_id)
    
    # Check permissions
    if request.user not in [escalation.buyer, escalation.dealer, escalation.yard_manager] and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to view this escalation.')
        return redirect('dashboard')
    
    return render(request, 'communication/escalation_detail.html', {'escalation': escalation})