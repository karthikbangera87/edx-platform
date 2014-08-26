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

def homework_badges(connector,badges_return,*args):
	#Homework tracker
	HW_count=0
	#setting of the badge issuer,program and course run by calling badgekit details         
        badge_issuer,badge_program,course_run=badgekit_details(courseid)
	#parsing through details in course summary and checking for sections which are graded and the format is Homework
        #currently the list of homeworks is mapped the the available badgeids i.e HW[1,2,3]= badges[4,7,8]
        #probably this mapping can be set while creating the course ie each homework is mapped to particular badge 
        for details in course_details:
                for section in details['sections']:
                        if section['graded']==True and section['format']=='Homework':
                                # access section total and determine result
                                earned=section['section_total'][0]
                                possible=section['section_total'][1]
                                store_result=earned/possible
                                #if the result is greater that 50% we issue a badge and proceed to next homework
                                if store_result >= 0.2:
                                        global badge_track
                                        # check to see if the badge is not issued else we create the badgeinstance
                                        if badge_track[args[0][HW_count]] =='not_issued':
                                                connector.create('instance',{'slug':'{}'.format(random.randrange(0,5000,1)),'email':useremail,'badgeId':args[0][HW_count]},system=currentbadgesystem(),issuer=badge_issuer,program=badge_program,badge=args[1][HW_count])


                                        HW_count+=1
                                else:
                                        HW_count+=1



        #return the badges earned and unearned details          
        return badges_return
	 
def badges_available_for_course(UserEmail,courseID,course_summary):
	global courseid,useremail,course_details
	#Python badgekit API connector object returned from the call to setupbadgekit()
	badgekit_connector=setupbadgekit()
	courseid=courseID
	useremail=UserEmail
	course_details=course_summary	
	#setting of the badge issuer,program and course run by calling badgekit details		
	badge_issuer,badge_program,course_run=badgekit_details(courseID)
	
	# keep track of badge ids and slug
	available_badge_ids=[] 	
	available_badge_slugs=[] 
	
	# return the badge earned and unearned details
	badges_return={'Earned':[],'Unearned':[]}
	
	# Us of connector object to list all badge available under the badgekit system for this issuer and program
	badges_available= badgekit_connector.list('badge',system=currentbadgesystem(),issuer=badge_issuer,program=badge_program)

	# extract badge ids and slugs from badges avaialable 
	for badge in badges_available['badges']:
		available_badge_ids.append(badge['id'])
		available_badge_slugs.append(badge['slug'])
	
	# call to badges_issued,intially in the first iteration value is empty since no badge is issued for the current user
	earned_list=badges_issued(badgekit_connector,badge_issuer,badge_program,UserEmail,available_badge_ids)	
	
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
	
	badges=homework_badges(badgekit_connector,badges_return,available_badge_ids,available_badge_slugs)

	return badges
