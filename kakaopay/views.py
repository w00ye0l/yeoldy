from django.shortcuts import render, redirect
import requests
from accounts.models import User
from cart.models import CartItem

# Create your views here.
def index(request):
    user = User.objects.get(pk=request.user.pk)

    #cart_item_name
    cart_items = list(CartItem.objects.filter(user_id=request.user.pk))
    first_item = str(cart_items[0])
    cart_quantity = int(len(cart_items))
    print(first_item)
    print(cart_quantity, type(cart_quantity))

    #첫 아이템 말고는 외 ~건으로 처리
    if cart_quantity == 1:
        cart_item_name = first_item
    else:
        cart_item_name = first_item + " 외 " + str(cart_quantity-1) + "건"

    #cart_total
    cart_total = 0
    for cart_item in cart_items:
        cart_total += cart_item.product.cost * cart_item.quantity

    if request.method == "POST":
        URL = 'https://kapi.kakao.com/v1/payment/ready'
        headers = {
            "Authorization": "KakaoAK " + "b2fcbb98f1cd8dbadcae7f2981acb9e3",   # 변경불가
            "Content-type": "application/x-www-form-urlencoded;charset=utf-8",  # 변경불가
        }
        params = {
            "cid": "TC0ONETIME",    # 테스트용 코드
            "partner_order_id": "1001",     # 주문번호
            "partner_user_id": "{}".format(user),    # 유저 아이디
            "item_name": "{}".format(cart_item_name),        # 구매 물품 이름
            "quantity": "{}".format(cart_quantity),                # 구매 물품 수량
            "total_amount": "{}".format(cart_total),        # 구매 물품 가격
            "tax_free_amount": "0",         # 구매 물품 비과세
            "approval_url": "http://127.0.0.1:8000/kakaopay/approval/",
            "cancel_url": "http://127.0.0.1:8000",
            "fail_url": "http://127.0.0.1:8000",
        }
        print(params)

        res = requests.post(URL, headers=headers, params=params)
        request.session['tid'] = res.json()['tid']      # 결제 승인시 사용할 tid를 세션에 저장
        next_url = res.json()['next_redirect_pc_url']   # 결제 페이지로 넘어갈 url을 저장
        return redirect(next_url)

    return render(request, 'kakaopay/index.html')

def approval(request):
    URL = 'https://kapi.kakao.com/v1/payment/approve'
    headers = {
        "Authorization": "KakaoAK " + "b2fcbb98f1cd8dbadcae7f2981acb9e3",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    params = {
        "cid": "TC0ONETIME",    # 테스트용 코드
        "tid": request.session['tid'],  # 결제 요청시 세션에 저장한 tid
        "partner_order_id": "1001",     # 주문번호
        "partner_user_id": "german",    # 유저 아이디
        "pg_token": request.GET.get("pg_token"),     # 쿼리 스트링으로 받은 pg토큰
    }

    res = requests.post(URL, headers=headers, params=params)
    # amount = res.json()['amount']['total']
    res = res.json()
    context = {
        'res': res,
        # 'amount': amount,
    }
    return render(request, 'kakaopay/approval.html', context)