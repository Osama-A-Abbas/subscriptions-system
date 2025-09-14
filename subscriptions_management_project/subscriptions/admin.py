from django.contrib import admin
from .models import Subscription, Category
from django.core.management import call_command

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "billing_cycle",
        "monthly_cost",
        "yearly_cost",
        "get_duration_display",
        "get_total_cost_display",
        "renewal_date",
        "is_active",
    )
    list_filter = ("billing_cycle", "is_active", "category")
    search_fields = ("name",)
    
    def get_duration_display(self, obj):
        """Display duration in a user-friendly format"""
        if obj.billing_cycle == 'monthly' and obj.duration_months:
            return f"{obj.duration_months} months"
        elif obj.billing_cycle == 'yearly' and obj.duration_years:
            return f"{obj.duration_years} years"
        return "No duration set"
    get_duration_display.short_description = "Duration"
    
    def get_total_cost_display(self, obj):
        """Display total cost for the entire duration"""
        total_cost = obj.get_total_cost()
        if total_cost:
            return f"${total_cost:.2f}"
        return "N/A"
    get_total_cost_display.short_description = "Total Cost"


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
    actions = ['seed_categories_action']
    
    def get_subcategories_count(self, obj):
        """Display the number of subcategories for this category."""
        if obj.pk:
            return obj.subcategories.count()
        return 0
    get_subcategories_count.short_description = "Subcategories"
    
    def seed_categories_action(self, request, queryset):
        """Admin action to seed categories."""
        call_command('seed_categories')
        self.message_user(request, 'Categories seeded successfully!')
    seed_categories_action.short_description = "Seed default categories"
    
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
    
