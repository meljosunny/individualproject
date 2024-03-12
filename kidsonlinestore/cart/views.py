from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from shop.models import Product
from cart.models import Cart,Account,Order
# Create your views here.

def cartview(request):
    sum=0
    u=request.user
    try:
        cart=Cart.objects.filter(user=u)
        for i in cart:
            sum += i.quantity*i.product.price
    except:
        pass
    return render(request,'cart.html',{'c':cart,'total':sum})

@login_required
def add_to_cart(request,p):
    product=Product.objects.get(name=p)
    u=request.user  #to get details of currently logined user
    try:
        cart=Cart.objects.get(user=u,product=product)
        if(cart.quantity<cart.product.stock):
            cart.quantity+=1
        cart.save()
    except:
        cart=Cart.objects.create(product=product,user=u,quantity=1)
        cart.save()


    return redirect('cart:cartview')


@login_required
def remove_from_cart(request,p):
    product=Product.objects.get(name=p)
    u=request.user
    try:
        cart=Cart.objects.get(user=u,product=product)
        if(cart.quantity>1):
            cart.quantity-=1

            cart.save()
        else:
            cart.delete()
    except:
        pass

    return redirect('cart:cartview')

@login_required
def delete_from_cart(request,p):
    product=Product.objects.get(name=p)
    u=request.user
    cart=Cart.objects.get(user=u,product=product)
    cart.delete()

    return redirect('cart:cartview')

def orderform(request):

    if(request.method=='POST'):
        a=request.POST['a']
        p=request.POST['p']
        n=request.POST['n']
        u=request.user
        cart=Cart.objects.filter(user=u)


        #total amount
        total = 0
        for i in cart:
            total+=i.quantity*i.product.price


        #checks whether user has sufficient amount in his account
        ac=Account.objects.get(acctnum=n)
        if(ac.amount>=total):
            ac.amount=ac.amount-total
            ac.save()

            for i in cart: #creates record in order table for each object in cart table for the current user
                o=Order.objects.create(user=u,product=i.product,address=a,phone=p,no_of_items=i.quantity,order_status="paid")
                o.save()
                i.product.stock=i.product.stock-i.quantity
                i.product.save()

            cart.delete() #clears the cart items for the current user
            msg="order placed successfully"
            return render(request,'orderdetail.html',{'m':msg})

        else:
            msg="Insufficient amount in User Amount.You cannot place order"
            return render(request,'orderdetail.html',{'m':msg})


    return render(request,'orderform.html')


def orderview(request):
    u=request.user
    o=Order.objects.filter(user=u)
    return render(request,'orderview.html',{'order':o})