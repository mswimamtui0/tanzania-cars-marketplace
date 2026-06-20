import os

# Template content for each file
templates = {
    'home.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Tanzania Cars Marketplace" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Welcome to Tanzania Cars Marketplace" %}</h1>
        <p>{% trans "Your car marketplace is running successfully!" %}</p>
        <a href="{% url 'car_list' %}" class="btn btn-primary">{% trans "View Cars" %}</a>
        <a href="{% url 'add_car' %}" class="btn btn-success">{% trans "Sell Your Car" %}</a>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'about.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "About Us" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "About Tanzania Cars Marketplace" %}</h1>
        <p>{% trans "We are Tanzania's leading car marketplace connecting buyers and sellers." %}</p>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'contact.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Contact Us" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Contact Us" %}</h1>
        <p>{% trans "Get in touch with our team." %}</p>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'terms.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Terms & Conditions" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Terms & Conditions" %}</h1>
        <p>{% trans "Please read our terms carefully." %}</p>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'privacy.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Privacy Policy" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Privacy Policy" %}</h1>
        <p>{% trans "We value your privacy." %}</p>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'profile.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Profile" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Your Profile" %}</h1>
        <p>{% trans "Welcome" %} {{ user.username }}!</p>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'registration/login.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Login" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-4">
                <h2 class="text-center">{% trans "Login" %}</h2>
                <form method="post">
                    {% csrf_token %}
                    {{ form.as_p }}
                    <button type="submit" class="btn btn-primary w-100">{% trans "Login" %}</button>
                </form>
                <p class="mt-3 text-center"><a href="{% url 'register' %}">{% trans "Create an account" %}</a></p>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'registration/register.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Register" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <h2 class="text-center">{% trans "Register" %}</h2>
                <form method="post">
                    {% csrf_token %}
                    {{ form.as_p }}
                    <button type="submit" class="btn btn-success w-100">{% trans "Register" %}</button>
                </form>
                <p class="mt-3 text-center"><a href="{% url 'login' %}">{% trans "Already have an account?" %}</a></p>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'cars/list.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Cars" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Available Cars" %}</h1>
        <div class="row">
            {% for car in page_obj %}
                <div class="col-md-4 mb-4">
                    <div class="card">
                        <div class="card-body">
                            <h5>{{ car.brand }} {{ car.model }}</h5>
                            <p>TSh {{ car.price|floatformat:0 }}</p>
                            <a href="{% url 'car_detail' car.id %}" class="btn btn-primary">{% trans "View" %}</a>
                        </div>
                    </div>
                </div>
            {% empty %}
                <p>{% trans "No cars found." %}</p>
            {% endfor %}
        </div>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'cars/detail.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{{ car.title }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{{ car.brand }} {{ car.model }}</h1>
        <p><strong>{% trans "Price" %}:</strong> TSh {{ car.price|floatformat:0 }}</p>
        <p><strong>{% trans "Year" %}:</strong> {{ car.year }}</p>
        <p><strong>{% trans "Mileage" %}:</strong> {{ car.mileage }} km</p>
        <p><strong>{% trans "Location" %}:</strong> {{ car.location }}</p>
        <a href="{% url 'car_list' %}" class="btn btn-secondary">{% trans "Back to Cars" %}</a>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'cars/add.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Add Car" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Add a Car" %}</h1>
        <form method="post" enctype="multipart/form-data">
            {% csrf_token %}
            {{ form.as_p }}
            <button type="submit" class="btn btn-success">{% trans "Add Car" %}</button>
        </form>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'cars/edit.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Edit Car" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Edit Car" %}</h1>
        <form method="post" enctype="multipart/form-data">
            {% csrf_token %}
            {{ form.as_p }}
            <button type="submit" class="btn btn-primary">{% trans "Save Changes" %}</button>
        </form>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'cars/delete_confirm.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Delete Car" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Delete Car" %}</h1>
        <p>{% trans "Are you sure you want to delete" %} {{ car.title }}?</p>
        <form method="post">
            {% csrf_token %}
            <button type="submit" class="btn btn-danger">{% trans "Yes, Delete" %}</button>
            <a href="{% url 'car_detail' car.id %}" class="btn btn-secondary">{% trans "Cancel" %}</a>
        </form>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'dealer/dashboard.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Dealer Dashboard" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Dealer Dashboard" %}</h1>
        <p>{% trans "Welcome" %} {{ user.username }}!</p>
        <div class="row">
            <div class="col-md-4">
                <div class="card text-white bg-primary mb-3">
                    <div class="card-body">
                        <h5>{% trans "Total Cars" %}</h5>
                        <h2>{{ total_cars }}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-white bg-success mb-3">
                    <div class="card-body">
                        <h5>{% trans "Available" %}</h5>
                        <h2>{{ available_cars }}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-white bg-danger mb-3">
                    <div class="card-body">
                        <h5>{% trans "Sold" %}</h5>
                        <h2>{{ sold_cars }}</h2>
                    </div>
                </div>
            </div>
        </div>
        <a href="{% url 'dealer_add_car' %}" class="btn btn-success">{% trans "Add New Car" %}</a>
        <a href="{% url 'dealer_cars' %}" class="btn btn-primary">{% trans "View My Cars" %}</a>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'dealer/cars.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "My Cars" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "My Cars" %}</h1>
        <div class="row">
            {% for car in page_obj %}
                <div class="col-md-4 mb-4">
                    <div class="card">
                        <div class="card-body">
                            <h5>{{ car.brand }} {{ car.model }}</h5>
                            <p>TSh {{ car.price|floatformat:0 }}</p>
                            <a href="{% url 'dealer_edit_car' car.id %}" class="btn btn-primary">{% trans "Edit" %}</a>
                            <a href="{% url 'dealer_delete_car' car.id %}" class="btn btn-danger">{% trans "Delete" %}</a>
                        </div>
                    </div>
                </div>
            {% empty %}
                <p>{% trans "No cars listed." %}</p>
            {% endfor %}
        </div>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'dealer/add_car.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Add Car" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Add Car" %}</h1>
        <form method="post" enctype="multipart/form-data">
            {% csrf_token %}
            {{ form.as_p }}
            <button type="submit" class="btn btn-success">{% trans "Add Car" %}</button>
        </form>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'dealer/edit_car.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Edit Car" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Edit Car" %}</h1>
        <form method="post" enctype="multipart/form-data">
            {% csrf_token %}
            {{ form.as_p }}
            <button type="submit" class="btn btn-primary">{% trans "Save Changes" %}</button>
        </form>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'dealer/delete_confirm.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Delete Car" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Delete Car" %}</h1>
        <p>{% trans "Are you sure?" %}</p>
        <form method="post">
            {% csrf_token %}
            <button type="submit" class="btn btn-danger">{% trans "Delete" %}</button>
            <a href="{% url 'dealer_cars' %}" class="btn btn-secondary">{% trans "Cancel" %}</a>
        </form>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'dealer/messages.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Messages" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Messages" %}</h1>
        <p>{% trans "Your messages will appear here." %}</p>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'dealer/commission.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Commission" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Commission Dashboard" %}</h1>
        <p>{% trans "Total Commission:" %} TSh {{ total_commission|floatformat:0 }}</p>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'yard/dashboard.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Yard Dashboard" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Yard Dashboard" %}</h1>
        <p>{% trans "Welcome" %} {{ user.username }}!</p>
        <a href="{% url 'yard_add_car' %}" class="btn btn-success">{% trans "Add Car" %}</a>
        <a href="{% url 'yard_pending_cars' %}" class="btn btn-warning">{% trans "Pending Cars" %}</a>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'yard/cars.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Yard Cars" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Yard Cars" %}</h1>
        <div class="row">
            {% for car in page_obj %}
                <div class="col-md-4 mb-4">
                    <div class="card">
                        <div class="card-body">
                            <h5>{{ car.brand }} {{ car.model }}</h5>
                            <p>TSh {{ car.price|floatformat:0 }}</p>
                        </div>
                    </div>
                </div>
            {% empty %}
                <p>{% trans "No cars." %}</p>
            {% endfor %}
        </div>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'yard/add_car.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Add Car" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Add Car to Yard" %}</h1>
        <form method="post" enctype="multipart/form-data">
            {% csrf_token %}
            {{ form.as_p }}
            <button type="submit" class="btn btn-success">{% trans "Add Car" %}</button>
        </form>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'yard/edit_car.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Edit Car" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Edit Car" %}</h1>
        <form method="post" enctype="multipart/form-data">
            {% csrf_token %}
            {{ form.as_p }}
            <button type="submit" class="btn btn-primary">{% trans "Save" %}</button>
        </form>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'yard/delete_confirm.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Delete Car" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Delete Car" %}</h1>
        <p>{% trans "Are you sure?" %}</p>
        <form method="post">
            {% csrf_token %}
            <button type="submit" class="btn btn-danger">{% trans "Delete" %}</button>
        </form>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'yard/pending.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Pending Cars" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Pending Cars" %}</h1>
        <div class="row">
            {% for car in cars %}
                <div class="col-md-4 mb-4">
                    <div class="card">
                        <div class="card-body">
                            <h5>{{ car.brand }} {{ car.model }}</h5>
                            <a href="{% url 'yard_approve_car' car.id %}" class="btn btn-success">{% trans "Approve" %}</a>
                            <a href="{% url 'yard_reject_car' car.id %}" class="btn btn-danger">{% trans "Reject" %}</a>
                        </div>
                    </div>
                </div>
            {% empty %}
                <p>{% trans "No pending cars." %}</p>
            {% endfor %}
        </div>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'admin/dashboard.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Admin Dashboard" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Admin Dashboard" %}</h1>
        <div class="row">
            <div class="col-md-3"><div class="card"><div class="card-body"><h5>{% trans "Total Cars" %}</h5><h2>{{ total_cars }}</h2></div></div></div>
            <div class="col-md-3"><div class="card"><div class="card-body"><h5>{% trans "Total Users" %}</h5><h2>{{ total_users }}</h2></div></div></div>
            <div class="col-md-3"><div class="card"><div class="card-body"><h5>{% trans "Dealers" %}</h5><h2>{{ total_dealers }}</h2></div></div></div>
            <div class="col-md-3"><div class="card"><div class="card-body"><h5>{% trans "Reports" %}</h5><h2>{{ total_reports }}</h2></div></div></div>
        </div>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'admin/users.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Users" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Users" %}</h1>
        <table class="table">
            <thead><tr><th>{% trans "Username" %}</th><th>{% trans "Email" %}</th><th>{% trans "Joined" %}</th></tr></thead>
            <tbody>
                {% for user in page_obj %}
                    <tr><td>{{ user.username }}</td><td>{{ user.email }}</td><td>{{ user.date_joined|date:"Y-m-d" }}</td></tr>
                {% empty %}
                    <tr><td colspan="3">{% trans "No users." %}</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'admin/cars.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Admin Cars" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "All Cars" %}</h1>
        <table class="table">
            <thead><tr><th>{% trans "Title" %}</th><th>{% trans "Price" %}</th><th>{% trans "Status" %}</th></tr></thead>
            <tbody>
                {% for car in page_obj %}
                    <tr><td>{{ car.title }}</td><td>TSh {{ car.price|floatformat:0 }}</td><td>{{ car.status }}</td></tr>
                {% empty %}
                    <tr><td colspan="3">{% trans "No cars." %}</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'admin/dealers.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Dealers" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Dealers" %}</h1>
        <table class="table">
            <thead><tr><th>{% trans "Business" %}</th><th>{% trans "Location" %}</th><th>{% trans "Verified" %}</th></tr></thead>
            <tbody>
                {% for dealer in dealers %}
                    <tr><td>{{ dealer.business_name }}</td><td>{{ dealer.location }}</td><td>{% if dealer.is_verified %}✅{% else %}❌{% endif %}</td></tr>
                {% empty %}
                    <tr><td colspan="3">{% trans "No dealers." %}</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'admin/yards.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Yards" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Yards" %}</h1>
        <table class="table">
            <thead><tr><th>{% trans "Name" %}</th><th>{% trans "Location" %}</th><th>{% trans "Capacity" %}</th></tr></thead>
            <tbody>
                {% for yard in yards %}
                    <tr><td>{{ yard.name }}</td><td>{{ yard.location }}</td><td>{{ yard.capacity }}</td></tr>
                {% empty %}
                    <tr><td colspan="3">{% trans "No yards." %}</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'buyer/dashboard.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Buyer Dashboard" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Buyer Dashboard" %}</h1>
        <p>{% trans "Welcome" %} {{ user.username }}!</p>
        <a href="{% url 'favorites_list' %}" class="btn btn-primary">{% trans "View Favorites" %}</a>
        <a href="{% url 'buyer_inspections' %}" class="btn btn-info">{% trans "View Inspections" %}</a>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'buyer/inspections.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Inspections" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "My Inspections" %}</h1>
        <p>{% trans "Your inspection requests will appear here." %}</p>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'favorites/list.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Favorites" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Your Favorites" %}</h1>
        <div class="row">
            {% for favorite in favorites %}
                <div class="col-md-4 mb-4">
                    <div class="card">
                        <div class="card-body">
                            <h5>{{ favorite.car.brand }} {{ favorite.car.model }}</h5>
                            <p>TSh {{ favorite.car.price|floatformat:0 }}</p>
                            <a href="{% url 'car_detail' favorite.car.id %}" class="btn btn-primary">{% trans "View" %}</a>
                        </div>
                    </div>
                </div>
            {% empty %}
                <p>{% trans "No favorites yet." %}</p>
            {% endfor %}
        </div>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'messages/detail.html': '''{% load i18n %}
<!DOCTYPE html>
<html>
<head>
    <title>{% trans "Message" %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    <div class="container mt-5">
        <h1>{% trans "Message" %}</h1>
        <p><strong>{% trans "From" %}:</strong> {{ message.sender.username }}</p>
        <p><strong>{% trans "Content" %}:</strong> {{ message.content }}</p>
        <a href="{% url 'home' %}" class="btn btn-secondary">{% trans "Back" %}</a>
    </div>
    {% include 'includes/footer.html' %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'includes/navbar.html': '''{% load i18n %}
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
        <a class="navbar-brand" href="{% url 'home' %}">🚗 {% trans "Tanzania Cars" %}</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav me-auto">
                <li class="nav-item"><a class="nav-link" href="{% url 'home' %}">{% trans "Home" %}</a></li>
                <li class="nav-item"><a class="nav-link" href="{% url 'car_list' %}">{% trans "Cars" %}</a></li>
                <li class="nav-item"><a class="nav-link" href="{% url 'about' %}">{% trans "About" %}</a></li>
                <li class="nav-item"><a class="nav-link" href="{% url 'contact' %}">{% trans "Contact" %}</a></li>
            </ul>
            <ul class="navbar-nav">
                {% if user.is_authenticated %}
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">{{ user.username }}</a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{% url 'profile' %}">{% trans "Profile" %}</a></li>
                            <li><a class="dropdown-item" href="{% url 'favorites_list' %}">{% trans "Favorites" %}</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><form action="{% url 'logout' %}" method="post">{% csrf_token %}<button type="submit" class="dropdown-item">{% trans "Logout" %}</button></form></li>
                        </ul>
                    </li>
                {% else %}
                    <li class="nav-item"><a class="nav-link" href="{% url 'login' %}">{% trans "Login" %}</a></li>
                    <li class="nav-item"><a class="nav-link btn btn-primary text-white" href="{% url 'register' %}">{% trans "Register" %}</a></li>
                {% endif %}
            </ul>
        </div>
    </div>
</nav>''',

    'includes/footer.html': '''{% load i18n %}
<footer class="bg-dark text-light py-4 mt-5">
    <div class="container text-center">
        <p>© 2026 {% trans "Tanzania Cars Marketplace" %}</p>
    </div>
</footer>''',

    'includes/language_switcher.html': '''{% load i18n %}
{% get_current_language as LANGUAGE_CODE %}
<form action="{% url 'set_language' %}" method="post" class="d-inline">
    {% csrf_token %}
    <input name="next" type="hidden" value="{{ request.get_full_path }}" />
    <select name="language" class="form-select form-select-sm" onchange="this.form.submit()">
        <option value="en" {% if LANGUAGE_CODE == 'en' %}selected{% endif %}>English</option>
        <option value="sw" {% if LANGUAGE_CODE == 'sw' %}selected{% endif %}>Kiswahili</option>
    </select>
</form>''',
}

# Create all template files
for path, content in templates.items():
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(f'templates/{path}'), exist_ok=True)
    
    # Write the file
    with open(f'templates/{path}', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'✅ Created templates/{path}')

print('\n🎉 All templates created successfully!')