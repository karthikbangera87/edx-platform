#def badges_available_for_course(course):
# TODO: really find badges
#return []

import badgekit.api

def badgekit_details(courseID):
                course_details=courseID.split('/')
                #{org}/{course}/{run} (for example, MITx/6.002x/2012_Fall).     

                return course_details
	 

def badges_available_for_course(UserEmail,courseID):

		a=badgekit.api.BadgeKitAPI('http://10.0.2.2:5000','hihello',defaults={'system':'badgekit'})
		badge_issuer,badge_program,course_run=badgekit_details(courseID)
		
		earned_list=[]
		available_list=[]
		badges_return={'Earned':[],'Unearned':[]}
		
		badges_available= a.list('badge',system='badgekit',issuer=badge_issuer,program=badge_program)
		
		for badge in badges_available['badges']:
			 available_list.append(badge['id'])
			
		raw_badges= a.list('email',system='badgekit',issuer=badge_issuer,program=badge_program,instance=UserEmail)
		for badge_instances in raw_badges['instances']:
				for item in available_list:
					if item == badge_instances['badge']['id']: 
						badges_return['Earned'].append(badge_instances['badge'])
						earned_list.append(badge_instances['badge']['id'])
					
		unearned_list=set(available_list) - set(earned_list)
				
		for badge in badges_available['badges']:
			for item in list(unearned_list):
				if badge['id'] == item:
					badges_return['Unearned'].append(badge)	
			
		return badges_return
