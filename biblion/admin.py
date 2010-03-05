from django.contrib import admin
from django.utils.functional import curry

from biblion.models import Post, Image
from biblion.forms import AdminPostForm
from biblion.utils import can_tweet

try:
    from photologue.models import Photo
    if isinstance(Image, Photo):
        from photologue.admin import PhotoAdmin as ImageAdmin
    else:
        # We are not using Photologue. Fall back
        raise ImportError
except ImportError:
    class ImageAdmin(admin.TabularInline):
        model = Image
        fields = ["image_path"]


class PostAdmin(admin.ModelAdmin):  
    list_display = ["title", "published_flag", "section", "featured"]
    list_filter = ["section"]
    form = AdminPostForm
    fieldsets = ([None,
                 {'fields': ["section",
                             "title",
                             "slug",
                             "author",
                             "content",
                             "publish",
                             "featured",
                              ]
                  }],
                  ['Below the fold',
                  {'classes': ('collapse',),
                   'fields': ['more_content', 'teaser_in_fulltext']},
                  ])

    if can_tweet():
        fields.append("tweet")
    prepopulated_fields = {"slug": ("title",)}

    if Photo:
        fieldsets[0][1]['fields'].append('images')
    else:
        fieldsets[1][1]['inlines'] = [ImageAdmin]

    def published_flag(self, obj):
        return bool(obj.published)
    published_flag.short_description = "Published"
    published_flag.boolean = True
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        request = kwargs.pop("request")
        if db_field.name == "author":
            ff = super(PostAdmin, self).formfield_for_dbfield(db_field, **kwargs)
            ff.initial = request.user.id
            return ff
        return super(PostAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    def get_form(self, request, obj=None, **kwargs):
        kwargs.update({
            "formfield_callback": curry(self.formfield_for_dbfield, request=request),
        })
        return super(PostAdmin, self).get_form(request, obj, **kwargs)
    
    def save_form(self, request, form, change):
        # this is done for explicitness that we want form.save to commit
        # form.save doesn't take a commit kwarg for this reason
        return form.save()


admin.site.register(Post, PostAdmin)
if not Photo: admin.site.register(Image)
