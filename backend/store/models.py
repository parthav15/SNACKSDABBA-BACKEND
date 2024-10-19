from django.db import models
from django.contrib.auth.models import AbstractUser

ROLE = {
    (1, 'Admin'),
    (2, 'Moderator'),
    (3, 'Customer Support Staff')
}

LOGIN_BY = {
    (1, 'General'),
    (2, 'Guest'),
    (3, 'Google'),
    (4, 'Facebook')
}

class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255, default="")
    last_name = models.CharField(max_length=255, default="")
    username = models.CharField(max_length=255, default="", blank=True, null=True)
    phone_number = models.CharField(max_length=255, default="", blank=True, null=True)
    dob = models.DateField(default=None, blank=True, null=True)
    marital_status = models.CharField(max_length=255, default="", blank=True, null=True)
    nationality = models.CharField(max_length=255, default="", blank=True, null=True)
    gender = models.CharField(max_length=255, default="", blank=True, null=True)
    country = models.CharField(max_length=255, default="", blank=True, null=True)
    city = models.CharField(max_length=255, default="", blank=True, null=True)
    address = models.TextField(default="", blank=True, null=True)
    zip_code = models.CharField(max_length=255, default="", blank=True, null=True)
    is_admin = models.BooleanField('Is admin', default=False)
    is_customer = models.BooleanField('Is customer', default=False)
    is_email = models.BooleanField('Is email', default=False)
    is_staff = models.BooleanField('Is staff', default=False)
    is_role = models.IntegerField(choices=ROLE, default=0)
    login_by = models.IntegerField(choices=LOGIN_BY, default=1)
    password = models.CharField(max_length=255, blank=True, null=True)
    two_factor = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pictures', default="", blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
    
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, default="", blank=True, null=True)
    description = models.TextField(default="", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, default="", blank=True, null=True)
    description = models.TextField(default="", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='products/', default="", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.id} by {self.user.username}"
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CartItem for {self.id} with {self.product.name} with quantity {self.quantity}"
    
class Coupon(models.Model):
    id = models.AutoField(primary_key=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code
    
class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} for {self.user.username}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"OrderItem {self.id} for {self.order.user.username} with {self.product.name} with quantity {self.quantity}"
    
class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipping_addresses')
    phone_number = models.CharField(max_length=255, default="", blank=True, null=True)
    address_line1 = models.CharField(max_length=255, default="", blank=True, null=True)
    address_line2 = models.CharField(max_length=255, default="", blank=True, null=True)
    city = models.CharField(max_length=255, default="", blank=True, null=True)
    state = models.CharField(max_length=255, default="", blank=True, null=True)
    country = models.CharField(max_length=255, default="", blank=True, null=True)
    postal_code = models.CharField(max_length=255, default="", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ShippingAddress {self.id} for {self.user.username}"
    
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=255, default="", blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.payment_id} for Order {self.order.id}"
    
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i,i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"
    
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s wishlist for {self.product.name}"
