#def badges_available_for_course(course):
    # TODO: really find badges
    #return []
import badgekit.api

def badges_available_for_course(courseID=None):
	
	a=badgekit.api.BadgeKitAPI('http://10.0.2.2:5000','hihello',defaults={'system':'badgekit'})
	if courseID is not None:
        	course_details=courseID.split('/')
		#{org}/{course}/{run} (for example, MITx/6.002x/2012_Fall).	
		
		org,course_name,course_run=course_details
		
		if org == 'edX' and course_name =='Open_DemoX':
			return a.list('badge',issuer='edX',program='Open_DemoX')
		
		if org == 'iuX' and course_name =='cs202x':
			return a.list('badge',issuer='iuX',program='cs202x')
		else:
			return None
	

	else:
		return courseID
