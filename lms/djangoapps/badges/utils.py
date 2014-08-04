#def badges_available_for_course(course):
# TODO: really find badges
#return []

import badgekit.api

def badges_available_for_course(UserEmail,courseID=None):

	a=badgekit.api.BadgeKitAPI('http://10.0.2.2:5000','hihello',defaults={'system':'badgekit'})
	if courseID is not None:
		course_details=courseID.split('/')
		#{org}/{course}/{run} (for example, MITx/6.002x/2012_Fall).	

		org,course_name,course_run=course_details
		earned_list=[]
		available_list=[]
		unearned_list=[]
		badges_return={'Earned':[],'Unearned':[]}
		#if org == 'edX' and course_name =='Open_DemoX':
		badges_available= a.list('badge',system='badgekit',issuer=org,program=course_name)
		slug_list=[]
		for badge in badges_available['badges']:
			 available_list.append(badge['id'])
			 slug_list.append(badge['slug'])
			
			
		for item in range(len(slug_list)):
			raw_badges= a.list('instance',system='badgekit',issuer=org,program=course_name,badge='{}'.format(slug_list[item]))
			for badge_instances in raw_badges['instances']:
				if UserEmail == badge_instances['email']:
					badges_return['Earned'].append(badge_instances['badge'])	
					earned_list.append(badge_instances['badge']['id'])
					
			
		unearned_list=set(available_list) - set(earned_list)
				
		for badge in badges_available['badges']:
			for item in list(unearned_list):
				if badge['id'] == item:
					badges_return['Unearned'].append(badge)	
			
		
				
						
		return badges_return
			#return earned[1][2]['email']	
			#raw_badges['instances'][0]['badge']['id']

	    	
		
		#return badges_return
		#if org == 'iuX' and course_name =='cs202x':
			# a.list('badge',issuer='iuX',program='cs202x')
		#else:
			#return None
	
		
	else:
		return courseID
