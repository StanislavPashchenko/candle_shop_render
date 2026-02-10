from django import forms
from django.utils import translation
from .models import Order


class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        lang = (translation.get_language() or 'uk')[:2]
        if 'payment_method' in self.fields:
            self.fields['payment_method'].required = True
            if lang == 'ru':
                self.fields['payment_method'].choices = [
                    ('card', 'Оплата картой'),
                    ('cod', 'Оплата наложенным платежом'),
                ]
            else:
                self.fields['payment_method'].choices = [
                    ('card', 'Оплата карткою'),
                    ('cod', 'Оплата накладеним платежем'),
                ]

    class Meta:
        model = Order
        fields = ['full_name', 'phone', 'email', 'city', 'payment_method', 'notes', 'agree_to_terms']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ПІБ',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+380...',
                'type': 'tel',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@email.com',
                'required': True
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Населений пункт',
                'required': True
            }),
            'payment_method': forms.RadioSelect(attrs={
                'required': True
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Нотатки (опціонально)',
                'rows': 3
            }),
            'agree_to_terms': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'required': True
            })
        }