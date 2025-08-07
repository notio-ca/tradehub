#from django.contrib.admin import ModelAdmin, StackedInline, TabularInline
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from django.utils.safestring import mark_safe

class ModelAdminBase(ModelAdmin):
    list_display = []
    search_fields = []
    list_filter = [] 
    inlines = []
    actions = []
    list_per_page = 25
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def edit(self, obj):
        return mark_safe("<span class='cursor-pointer bg-primary-600 text-xs rounded px-4 py-1 text-white'>Edit</span>")
    edit.short_description = " "

    def get_list_display(self, request):
        list_display = super().get_list_display(request)

        if list_display == [] or list_display == ('__str__',):
            list_display = [field.name for field in self.model._meta.fields if (field.name != "id" and field.name != "key" and field.name != "is_active" and field.name != "date_create" and field.name != "date_update")]
            list_display.insert(0, "edit")
        return list_display

    def get_search_fields(self, request):
        #print(self.search_fields)
        #if self.search_fields == []:
        #self.search_fields = []
        for field in self.model._meta.fields:
            if field.name in "|key|": continue
            #print(field.name)
            #print(str(field.__class__))
            if "CharField" in str(field.__class__) or "TextField" in str(field.__class__) or "IntegerField" in str(field.__class__) or "JSONField" in str(field.__class__):
                if not field.name in self.search_fields:
                    self.search_fields.append(field.name)
        #print(self.search_fields)
        return self.search_fields

    def get_queryset(self, request): 
        qs = super().get_queryset(request)
        #qs = qs.filter(user=request.user)   
        return qs
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_key in form.base_fields:
            form_field = form.base_fields[field_key]
            #print(form_field.widget)
            if "Textarea" in str(form_field.widget): form_field.widget.attrs.update({'rows': '3'})
        # form.base_fields['field_1'].queryset = MODEL.objects.filter(user=request.user)
        # form.base_fields['field_2'].widget.attrs.update({'rows': '3'})
        return form

    def changelist_view(self, request, extra_context={}): 
        extra_context['title'] = self.model._meta.verbose_name
        return super().changelist_view(request, extra_context)

class ModelInLineBase(TabularInline):
    hide_title = True
    tab = True
    extra = 0 

class ModelInLineVerticalBase(StackedInline):
    hide_title = True
    tab = True
    extra = 0 
