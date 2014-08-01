#def badges_available_for_course(course):
    # TODO: really find badges
    #return []
import badgekit.api,collections



def badges_available_for_course(UserEmail,courseID=None):
	
	a=badgekit.api.BadgeKitAPI('http://10.0.2.2:5000','hihello',defaults={'system':'badgekit'})
	if courseID is not None:
        	course_details=courseID.split('/')
		#{org}/{course}/{run} (for example, MITx/6.002x/2012_Fall).	
		
		org,course_name,course_run=course_details
		
		if org == 'edX' and course_name =='Open_DemoX':
			raw_badges= a.list('badge',issuer='edX',program='Open_DemoX')
	
	        badges_return={'Unearned':[]}	
	        for badge in raw_badges['badges']:	
			badge['is_earned']='False'
		
		for badgeid in raw_badges['badges']:
			if badgeid['id']==7:
				badgeid['is_earned']='True'
				badges_return['Earned']=[]
				badges_return['Earned'].append(badgeid)
			else:
			
				badges_return['Unearned'].append(badgeid)
		
		#for badges in raw_badges['badges']:
			#if badges['is_earned']=='True':
				#badges_return={'Earned':badges}
			
		
			
		
		return badges_return
		
		#if raw_badges['badges'][0]['is_earned']=='True':
			#badges_return={'Earned':raw_badges['badges'][0]}
		
		
		#badges_return['Unearned']=raw_badges['badges'][1]
		#return badges_return
		
		 		
	 	
			
		#if org == 'iuX' and course_name =='cs202x':
			# a.list('badge',issuer='iuX',program='cs202x')
		#else:
			#return None
	

	else:
		return courseID
