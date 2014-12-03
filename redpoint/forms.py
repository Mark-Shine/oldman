from django import forms
from django.forms.models import modelform_factory
from django.core.urlresolvers import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.layout import Layout, Fieldset, Field

from redpoint.models import Oldman
# class CheckInForm(forms.Form):

#     avatar = forms.FileField()

# CheckInForm = modelform_factory(Oldman, fields=('name', 'avatar'))

class CheckInForm(forms.Form):
    name = forms.CharField(
        label=u"姓名",
        required=False,)
    bed = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput(),
        )    
    room = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput(),
        )    

        # class Meta:
    #     model = Oldman
    #     fields = ("name",)

    def __init__(self, *args, **kwargs):
        super(CheckInForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-checkinForm'
        self.helper.form_class = 'form'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse("checkin")
        self.helper.add_input(Submit('submit', u'登记'))


class MessagesForm(forms.Form):
    payload = forms.CharField(label=u"消息", required=True)
    # start_t = forms.TimeField(label=u"开始时间", required=True)
    # end_t = forms.TimeField(label=u"结束时间", required=True)

    def __init__(self, *args, **kwargs):
        super(MessagesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-messageForm'
        self.helper.form_class = 'form'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse("add_message")
        self.helper.add_input(Submit('submit', u'登记'))





