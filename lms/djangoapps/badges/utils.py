#def badges_available_for_course(course):
# TODO: really find badges
#return []

import badgekit.api,random


# global badge tracker to keep track of issued and not issued badges
badge_track={}

def currentbadgesystem():
	#currently hardcoded,will change later as per the system set
	default='badgekit'
	return default

def setupbadgekit():

	return badgekit.api.BadgeKitAPI('http://10.0.2.2:5000','hihello',defaults={'system':currentbadgesystem()})


#set_badge_track method takes the available badges as arguement and updates the badge track items to not_issued
def set_badge_track(avail):
	global badge_track
	dummy_dictionary={}
	for item in avail:
		dummy_dictionary[item]='not_issued'
	
	badge_track=dummy_dictionary

	return 


#keeps track of badges issued
def badges_issued(obj,badge_issuer,badge_program,UserEmail,available_badge_ids):

	 
	earned=[]	
	#listing the badgeinstances by email[current user]
	raw_badges=obj.list('email',system=currentbadgesystem(),issuer=badge_issuer,program=badge_program,instance=UserEmail)
	if raw_badges:
        	for badge_instances in raw_badges['instances']:
                	for item in available_badge_ids:
                        	if item == badge_instances['badge']['id']:
         	               		earned.append(badge_instances['badge']['id'])
			       
	# setting the badge tracker
	set_badge_track(available_badge_ids)
	
	# check to see if there are earned badges, then reset the badge tracker to indicate the earned badge
	if earned:
		global badge_track
		for item in earned:
			badge_track[item]='issued'
	
	#return earned list
	return earned

def badgekit_details(courseID):
	course_details=courseID.split('/')
    	#{org}/{course}/{run} (for example, MITx/6.002x/2012_Fall).     
	return course_details
	 

def badges_available_for_course(UserEmail,courseID,course_summary):

	#Python badgekit API connector object returned from the call to setupbadgekit()
	a=setupbadgekit()
	
	#setting of the badge issuer,program and course run by calling badgekit details		
	badge_issuer,badge_program,course_run=badgekit_details(courseID)
	
	# keep track of badge ids and slug
	available_badge_ids=[] 	
	available_badge_slugs=[] 
	
	# return the badge earned and unearned details
	badges_return={'Earned':[],'Unearned':[]}
	
	# track of Homework currently (may change)
	HW_count=0
	
	# Us of connector object to list all badge available under the badgekit system for this issuer and program
	badges_available= a.list('badge',system='badgekit',issuer=badge_issuer,program=badge_program)

	# extract badge ids and slugs from badges avaialable 
	for badge in badges_available['badges']:
		available_badge_ids.append(badge['id'])
		available_badge_slugs.append(badge['slug'])
	
	# call to badges_issued,intially in the first iteration value is empty since no badge is issued for the current user
	earned_list=badges_issued(a,badge_issuer,badge_program,UserEmail,available_badge_ids)	
	
	# if earned_list is empty we set all unearned badges to the available badges for the course
	if not earned_list:
			for badge in badges_available['badges']:	
				badges_return['Unearned'].append(badge)
	# else we check for the global badge track for issued badges and update the earned and unearned badges
	else:
			for item in badge_track:
                                if badge_track[item] == 'issued':
                                       for badge in badges_available['badges']:
				       		if item == badge['id']:
							badges_return['Earned'].append(badge)
				else:
				       for badge in badges_available['badges']:
						if item == badge['id']:
							badges_return['Unearned'].append(badge)
	
	#parsing through details in course summary and cehcking for sections which are graded and the format is Homework
	#currently the list of homeworks is mapped the the available badgeids i.e HW[1,2,3]= badges[4.7.8]
	#probably this mapping can be set while creating the course ie each homework is mapped to particular badge 
	for details in course_summary:
		for section in details['sections']:
			if section['graded']==True and section['format']=='Homework':
				# access section total and determine result
				earned=section['section_total'][0]
				possible=section['section_total'][1]
              			store_result=earned/possible
				#if the result is greater that 50% we issue a badge and proceed to next homework
              			if store_result >= 0.5:
				 	global badge_track
					# check to see if the badge is not issued else we create the badgeinstance
					if badge_track[available_badge_ids[HW_count]] =='not_issued':
						a.create('instance',{'slug':'{}'.format(random.randrange(0,5000,1)),'email':UserEmail,'badgeId':available_badge_ids[HW_count]},system='badgekit',issuer=badge_issuer,program=badge_program,badge=available_badge_slugs[HW_count])		
	
							
					HW_count+=1
				else:
					HW_count+=1
					
	
 
        #return the badges earned and unearned details		
	return badges_return
