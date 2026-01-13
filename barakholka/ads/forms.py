from django import forms
from django.forms import inlineformset_factory

from ads import models
from ads.models import Ads, AdsImage


class AdsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.widgets.TextInput, forms.widgets.Textarea, forms.widgets.Select, forms.widgets.NumberInput)):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field.widget, forms.widgets.ClearableFileInput):
                field.widget.attrs['class'] = 'form-control-file'

    class Meta:
        model = Ads
        exclude = ('seller',)


class AdsImageForm(forms.ModelForm):
    order = forms.IntegerField(
        label='Порядок',
        min_value=1,
        initial=1,
        help_text='Чем меньше число, тем выше изображение в списке'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'image':
                field.widget.attrs['class'] = 'form-control-file'
            elif isinstance(field.widget, (forms.widgets.TextInput, forms.widgets.NumberInput)):
                field.widget.attrs['class'] = 'form-control'
            elif field_name == 'is_main':
                field.required = False

    class Meta:
        model = AdsImage
        fields = ('image', 'is_main', 'order')


class AdsImageFormSet(inlineformset_factory(Ads, AdsImage, form=AdsImageForm, extra=0, can_delete=False)):
    def clean(self):
        super().clean()
        # Получаем количество валидных форм с изображениями
        valid_forms_with_images = [form for form in self.forms if form.is_valid() and form.cleaned_data.get('image')]

        # Для нескольких изображений проверяем, что хотя бы одно отмечено как основное
        if len(valid_forms_with_images) > 1:
            has_main_image = any(form.cleaned_data.get('is_main', False) for form in valid_forms_with_images)
            if not has_main_image:
                raise forms.ValidationError('Необходимо выбрать хотя бы одно основное изображение.')

    def save(self, commit=True):
        instances = super().save(commit=False)

        # Автоматически делаем первое изображение основным, если нет выбранного основного
        valid_instances = [instance for instance in instances if instance.image]
        if valid_instances:
            has_main = any(instance.is_main for instance in valid_instances)
            if not has_main:
                # Если ничего не выбрано, делаем первое изображение основным
                valid_instances[0].is_main = True

        if commit:
            for instance in instances:
                instance.save()
        return instances
