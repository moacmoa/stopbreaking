def displayRequestDetails(r, resp=True, req=True):
	print("--== INFOS REQUEST [{}] ==--".format(r.request.method))
	print("\t- URL : "+r.url)
	print("\t- STATUS : {}".format(r.status_code))
	
	if resp:
		print("\t- Response Headers :")
		for key, val in r.headers.iteritems():
			print("\t\t {} : {}".format(key, val))
	if req:
		print("\t- Request Headers :")
		for key, val in r.request.headers.iteritems():
			print("\t\t {} : {}".format(key, val))
    # print(r.request.__dict__)