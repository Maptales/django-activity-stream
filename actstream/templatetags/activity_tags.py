from django.template import Variable, Library, Node, TemplateSyntaxError, TemplateDoesNotExist
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from actstream.models import Action, Follow, target_stream, actor_stream, model_stream, user_stream

class DisplayActionLabel(Node):
    def __init__(self, actor, varname=None):
        self.actor = Variable(actor)
        self.varname = varname
        
    def render(self, context):
        actor_instance = self.actor.resolve(context)
        try:
            user = Variable("request.user").resolve(context)
        except:
            user = None
        try:
            if user and user == actor_instance.user:
                result=" your "
            else:
                result = " %s's " % (actor_instance.user.get_full_name() or actor_instance.user.username)
        except ValueError:
            result = ""
        result += actor_instance.get_label()
        if self.varname is not None:
            context[self.varname] = result
            return ""
        else:
            return result

class DisplayAction(Node):
    def __init__(self, action, varname=None):
        self.action = Variable(action)
        self.varname = varname
        
    def render(self, context):
        action_instance = self.action.resolve(context)
        try:
            action_output = render_to_string(('activity/%(verb)s/action.html' % { 'verb':action_instance.verb.replace(' ','_') }),{ 'action':action_instance },context)
        except TemplateDoesNotExist:
            action_output = render_to_string(('activity/action.html'),{ 'action':action_instance },context)
        if self.varname is not None:
            context[self.varname] = action_output
            return ""
        else:
            return action_output        
        
class DisplayActionShort(Node):
    def __init__(self, action, varname=None):
        self.action = Variable(action)
        self.varname = varname
        
    def render(self, context):
        action_instance = self.action.resolve(context)
        try:
            action_output = render_to_string(('activity/%(verb)s/action.html' % { 'verb':action_instance.verb.replace(' ','_') }),{ 'hide_actor':True, 'action':action_instance },context)
        except TemplateDoesNotExist:
            action_output = render_to_string(('activity/action.html'),{ 'hide_actor':True, 'action':action_instance },context)
        if self.varname is not None:
            context[self.varname] = action_output
            return ""
        else:
            return action_output        
        
class DisplayGroupedActions(Node):
    def __init__(self, actions, varname=None):
        self.actions = Variable(actions)
        self.varname = varname
        
    def render(self, context):
        actions_instance = self.action.resolve(context)
        try:
            action_output = render_to_string(('activity/%(verb)s/grouped.html' % { 'verb':actions_instance[0].verb }),{ 'actions':actions_instance })
        except TemplateDoesNotExist:
            action_output = render_to_string(('activity/grouped.html'),{ 'actions':actions_instance })
        if self.varname is not None:
            context[self.varname] = action_output
            return ""
        else:
            return action_output        
        
def do_print_action(parser, token):
    bits = token.contents.split()
    if len(bits) > 3:
        if len(bits) != 4:
            raise TemplateSyntaxError, "Accepted formats {% display_action [action] %} or {% display_action [action] as [var] %}"
        if bits[2] != 'as':
            raise TemplateSyntaxError, "Accepted formats {% display_action [action] %} or {% display_action [action] as [var] %}"
        return DisplayAction(bits[1],bits[3])
    else:
        return DisplayAction(bits[1])
        
def do_print_action_short(parser, token):
    bits = token.contents.split()
    if len(bits) > 3:
        if len(bits) != 4:
            raise TemplateSyntaxError, "Accepted formats {% display_action [action] %} or {% display_action [action] as [var] %}"
        if bits[2] != 'as':
            raise TemplateSyntaxError, "Accepted formats {% display_action [action] %} or {% display_action [action] as [var] %}"
        return DisplayActionShort(bits[1],bits[3])
    else:
        return DisplayActionShort(bits[1])
        
def do_print_grouped_actions(parser, token):
    bits = token.contents.split()
    if len(bits) > 3:
        if len(bits) != 4:
            raise TemplateSyntaxError, "Accepted formats {% display_grouped_actions [action] %} or {% display_action [action] as [var] %}"
        if bits[2] != 'as':
            raise TemplateSyntaxError, "Accepted formats {% display_grouped_actions [action] %} or {% display_action [action] as [var] %}"
        return DisplayAction(bits[1],bits[3])
    else:
        return DisplayAction(bits[1])
        
def do_print_action_label(parser, token):
    bits = token.contents.split()
    if len(bits) > 3:
        if len(bits) != 4:
            raise TemplateSyntaxError, "Accepted formats {% action_label [action] %} or {% action_label [action] as [var] %}"
        if bits[2] != 'as':
            raise TemplateSyntaxError, "Accepted formats {% action_label [action] %} or {% action_label [action] as [var] %}"
        return DisplayActionLabel(bits[1],bits[3])
    else:
        return DisplayActionLabel(bits[1])
    


register = Library()


@register.inclusion_tag("activity/follow_unfollow.html")
def follow_unfollow(actor, user):
    # check if following already
    ctype = ContentType.objects.get_for_model(actor)
    is_following = Follow.objects.is_following(actor, user)
    return {"actor": actor, "ctype":ctype, "user":user, "is_following":is_following}

@register.inclusion_tag("activity/activity_stream.html")
def global_stream(offset, count):
    return {"actions": Action.objects.all().order_by('-timestamp')[offset:count]}

# shows actions that have been done TO an object
@register.inclusion_tag("activity/activity_stream.html")
def show_target_stream(target, offset=0, count=30):
    return {"actions": target_stream(target)}

@register.inclusion_tag("activity/activity_stream.html")
def show_user_stream(user, offset=0, count=30):
    return {"actions": user_stream(user)}
    
@register.inclusion_tag("activity/activity_stream.html")
def show_actor_stream(actor, offset=0, count=30):
    return {"actions": actor_stream(actor)}

@register.inclusion_tag("activity/activity_stream.html")
def show_model_stream(model, offset=0, count=30):
    return {"actions": model_stream(model)}

@register.inclusion_tag("activity/followers.html")
def show_followers(actor, count=20):
    ctype = ContentType.objects.get_for_model(actor)
    follows = Follow.objects.filter(content_type=ctype, object_id=actor.pk)
    if count:
        follows = follows[0:count]
    return {'followers': (f.user for f in follows), 'actor':actor}

@register.inclusion_tag("activity/followers.html")
def show_following(actor, content_type=None, count=20):
    follows = Follow.objects.filter(user=actor)
    if count:
        follows = follows[0:count]
    return {'followers': (f.actor for f in follows), 'actor':actor}
    
register.tag('display_action', do_print_action)
register.tag('display_action_short', do_print_action_short)
register.tag('display_grouped_actions', do_print_grouped_actions)
register.tag('action_label', do_print_action_label)


# just changing it to make it different