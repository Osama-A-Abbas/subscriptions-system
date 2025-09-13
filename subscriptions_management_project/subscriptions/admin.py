from django.contrib import admin
from .models import Subscription, Category

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "billing_cycle",
        "monthly_cost",
        "yearly_cost",
        "renewal_date",
        "is_active",
    )
    list_filter = ("billing_cycle", "is_active", "category")
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "parent",
        "get_subcategories_count",
    )
    list_filter = ("parent",)
    search_fields = ("name", "description")
    
    def get_subcategories_count(self, obj):
        """Display the number of subcategories for this category."""
        return obj.subcategories.count()
    get_subcategories_count.short_description = "Subcategories"
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Customize the parent field dropdown to show hierarchical structure."""
        if db_field.name == "parent":
            # Exclude the current object from parent choices to prevent self-reference
            if hasattr(request, '_obj_') and request._obj_:
                kwargs["queryset"] = Category.objects.exclude(pk=request._obj_.pk)
            else:
                kwargs["queryset"] = Category.objects.all()
            
            # Order by name for better UX
            kwargs["queryset"] = kwargs["queryset"].order_by("name")
            
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_form(self, request, obj=None, **kwargs):
        """Store the current object for use in formfield_for_foreignkey."""
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)
