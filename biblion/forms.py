from datetime import datetime

from django import forms

from biblion.creole_parser import parse, BiblionHtmlEmitter
from biblion.models import Post, Revision
from biblion.utils import can_tweet


class AdminPostForm(forms.ModelForm):
    
    title = forms.CharField(
        max_length = 90,
        widget = forms.TextInput(
            attrs = {"style": "width: 50%;"},
        ),
    )
    slug = forms.CharField(
        widget = forms.TextInput(
            attrs = {"style": "width: 50%;"},
        )
    )
    content = forms.CharField(
        widget = forms.Textarea(
            attrs = {"style": "width: 80%;"},
        ),
        help_text = u"Content that will be displayed on the front page. Could be a the whole post or a teaser.",
    )
    more_content = forms.CharField(
        widget = forms.Textarea(
            attrs = {"style": "width: 80%; height: 300px;"},
        ),
        help_text = u'Content that will be displayed "below the fold" after a "Read More" link.',
    )
    publish = forms.BooleanField(
        required = False,
        help_text = u"Checking this will publish this article on the site",
    )
    featured = forms.BooleanField(
        required = False,
        help_text = u"Checking this will include this article on the front page",
    )
    teaser_in_fulltext = forms.BooleanField(
        required = False,
        help_text = u"Checking this will cause the full-text feed and display to include the teaser content above, followed by the content below",
    )
    if can_tweet():
        tweet = forms.BooleanField(
            required = False,
            help_text = u"Checking this will send out a tweet for this post",
        )
    
    class Meta:
        model = Post
    
    def __init__(self, *args, **kwargs):
        super(AdminPostForm, self).__init__(*args, **kwargs)
        
        post = self.instance
        
        # grab the latest revision of the Post instance
        latest_revision = post.latest()
        
        if latest_revision:
            # set initial data from the latest revision
            self.fields["teaser"].initial = latest_revision.teaser
            self.fields["content"].initial = latest_revision.content
        
            # @@@ can a post be unpublished then re-published? should be pulled
            # from latest revision maybe?
            self.fields["publish"].initial = bool(post.published)
        
    def save(self):
        post = super(AdminPostForm, self).save(commit=False)
        
        if post.pk is None:
            if self.cleaned_data["publish"]:
                post.published = datetime.now()
        else:
            if Post.objects.filter(pk=post.pk, published=None).count():
                if self.cleaned_data["publish"]:
                    post.published = datetime.now()
        
        post.teaser_html = parse(self.cleaned_data["teaser"], emitter=BiblionHtmlEmitter)
        post.content_html = parse(self.cleaned_data["content"], emitter=BiblionHtmlEmitter)
        post.updated = datetime.now()
        post.save()
        
        r = Revision()
        r.post = post
        r.title = post.title
        r.teaser = self.cleaned_data["teaser"]
        r.content = self.cleaned_data["content"]
        r.author = post.author
        r.updated = post.updated
        r.published = post.published
        r.save()
        
        if can_tweet() and self.cleaned_data["tweet"]:
            post.tweet()
        
        return post
