from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView
from .models import Business, Profile, Messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Create your views here.

def home(request):
    return render(request, 'home.html')


#===========================================================================================================
# Messages

@login_required
def inbox(request):
    """Display all conversations for the current user"""
    user = request.user
    
    # Get all msgs involving the user
    sent_messages = Messages.objects.filter(sender=user)
    received_messages = Messages.objects.filter(receiver=user)
    
    contact_ids = set()
    for msg in sent_messages:
        contact_ids.add(msg.receiver.id)
    for msg in received_messages:
        contact_ids.add(msg.sender.id)
    
    conversations = []
    for contact_id in contact_ids:
        contact = User.objects.get(id=contact_id)
        
        # Get latest message in conversation 
        sent = Messages.objects.filter(sender=user, receiver=contact).order_by('-timestamp').first()
        received = Messages.objects.filter(sender=contact, receiver=user).order_by('-timestamp').first()
        
        # Determine which message is more recent
        if sent and received:
            latest_message = sent if sent.timestamp > received.timestamp else received
        elif sent:
            latest_message = sent
        else:
            latest_message = received
        
        # Count unread messages from this contact
        unread_count = Messages.objects.filter(
            sender=contact,
            receiver=user,
            is_read=False
        ).count()
        
        conversations.append({
            'contact': contact,
            'latest_message': latest_message,
            'unread_count': unread_count,
        })
    
    conversations.sort(key=lambda x: x['latest_message'].timestamp if x['latest_message'] else 0, reverse=True)
    
    total_unread = Messages.objects.filter(receiver=user, is_read=False).count()
    
    return render(request, 'main_app/inbox.html', {
        'conversations': conversations,
        'total_unread': total_unread,
    })


@login_required
def conversation(request, user_id):
    """Display conversation thread with a specific user"""
    user = request.user
    other_user = get_object_or_404(User, id=user_id)
    
    sent_messages = Messages.objects.filter(sender=user, receiver=other_user)
    received_messages = Messages.objects.filter(sender=other_user, receiver=user)
    
    # Combine &&& sort by timestamp
    messages = list(sent_messages) + list(received_messages)
    messages.sort(key=lambda x: x.timestamp)
    
    unread_messages = Messages.objects.filter(
        sender=other_user,
        receiver=user,
        is_read=False
    )
    for msg in unread_messages:
        msg.is_read = True
        msg.save()
    
    # Get total unread count for navbar
    total_unread = Messages.objects.filter(receiver=user, is_read=False).count()
    
    return render(request, 'main_app/conversation.html', {
        'messages': messages,
        'other_user': other_user,
        'total_unread': total_unread,
    })


@login_required
def send_message(request, receiver_id):
    """Send a message to another user"""
    if request.method == 'POST':
        receiver = get_object_or_404(User, id=receiver_id)
        content = request.POST.get('content', '').strip()
        
        if content and len(content) <= 1000:
            Messages.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content,
            )
            return redirect('conversation', user_id=receiver_id)
        else:
            # Return error
            return redirect('conversation', user_id=receiver_id)
    
    return redirect('inbox')


def signup(request):
    error_message=''
    if request.method =='POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save()
            login(request,user)
            return redirect('/profile/create')
        else:
            error_message = 'Invalid signup - try again'
    else:
        form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)


#===========================================================================================================
#Profile
class ProfileCreate(CreateView):
    model = Profile
    fields = ["image", "role"]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.role == Profile.Role.BUSINESS_OWNER:
            return reverse("create_business")
        return reverse("home")

class ProfileDetail(DetailView):
    model = Profile
    template_name = 'main_app/profile_detail.html'

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

#===========================================================================================================
#Business
class BusinessCreate(CreateView):
    model = Business
    fields = ['name', 'description', 'category']
    success_url = '/'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class BusinessDetail(DetailView):
    model = Business
    template_name = 'main_app/business_detail.html'

    def get_object(self):
        return Business.objects.get(owner = self.request.user)
