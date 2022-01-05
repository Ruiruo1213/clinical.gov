import re

import re

test_string = 'a1b2cdefg'

matched = re.match("[a-z][0-9][a-z][0-9]+", test_string)
is_match = bool(matched)


# FUNCTIONs -----------------------------------------------------------------
# This function matches an intervention/arm with the route of administration terms
def  rte_admin_match(desc, oral_cond=NULL, transdermal_cond=NULL, injection_cond=NULL):
    if !oral_cond:
        oral_cond = (re.match('tablet|capsule|syrup|pill|drop',desc.lower()) or \
                     re.match( 'per os|(^|[^a-z]|\\s|[[:punct:]])po([^a-z]|\\s|$|[[:punct:]])|(^|[^a-z]|\\s|[[:punct:]])oral([^a-z]|\\s|$|[[:punct:]])|(^|[^a-z]|\\s|[[:punct:]])orally([^a-z]|\\s|$|[[:punct:]])|by mouth|sublingual',
       , desc.lower())

    if !transdermal_cond:
        transdermal_cond = re.match('patch|ointment|salve|cream|sticker|topical|occlusive dressing', desc.lower())

    if !injection_cond:
        injection_cond = ((re.match( '[^a-z]inject|[^a-z]infus|injected|injection|infusion|iv injection|im injection|sc injection|solution for infusion|powder for reconstitution|parenteral',
      , desc.lower()) or
       re.match('by vein|subcutaneous|intramuscular|intradermal|syringe driver|infusion pump|infusion|intravenous|(^|[^a-z]|\\s|[[:punct:]])iv([^a-z]|\\s|$|[[:punct:]])|(^|[^a-z]|\\s|[[:punct:]])im([^a-z]|\\s|$|[[:punct:]])|(^|[^a-z]|\\s|[[:punct:]])sc([^a-z]|\\s|$|[[:punct:]])|(^|[^a-z]|\\s|[[:punct:]])id([^a-z]|\\s|$|[[:punct:]])|parenteral',
                             desc.lower()) or
       re.match('\\d\\s?mg/ml(\\s|[[:punct:]]|$)|\\d\\s?g/l(\\s|[[:punct:]]|$)|\\d\\s?ml(\\s|[[:punct:]]|$)|\\d\\s?l(\\s|[[:punct:]]|$)|\\d\\s?dl(\\s|[[:punct:]]|$)',
                                                                   desc.lower()) or
       re.match('[a-z]mab(\\s|[[:punct:]]|$)|(^|[^a-z]|\\s|[[:punct:]])mab([^a-z]|\\s|$|[[:punct:]])|monoclonal antibod',
                            desc.lower())) and
                         (!re.match('grade iv', desc.lower())))
    if oral_cond:
        if transdermal_cond:
            return ['oral', 'transdermal']
        elif injection_cond:
            return ['oral', 'injection']
        elif injection_cond and transdermal_cond:
            return ['oral', 'injection', 'transdermal']
        else:
            return ['oral']
    elif transdermal_cond:
        if oral_cond:
            return ['oral', 'transdermal']
        elif injection_cond:
            return ['injection', 'transdermal']
        elif oral_cond and injection_cond:
            return ['oral', 'injection', 'transdermal']
        else:
            return ['transdermal']
    elif injection_cond:

        if oral_cond:
            return ['oral', 'injection']
        elif transdermal_cond:
            return ['injection', 'transdermal']
        elif oral_cond and transdermal_cond:
            return ['oral', 'injection', 'transdermal']
        else:
            return ['injection']
    else:
        return ['unknown']


def classify_rte_admin(trial):
    rte_arms_desc = rte_admin_match(trial['arms_desc'], oral_cond=NULL, transdermal_cond=NULL, injection_cond=NULL)
    rte_arms_title = rte_admin_match(trial['arms_title'], oral_cond=NULL, transdermal_cond=NULL, injection_cond=NULL)
    rte_interventions_desc = rte_admin_match(trial['interventions_desc'], oral_cond=NULL, transdermal_cond=NULL, injection_cond=NULL)
    rte_interventions_name = rte_admin_match(trial['interventions_name'], oral_cond=NULL, transdermal_cond=NULL, injection_cond=NULL)
    rte = rte_arms_desc.append(rte_arms_title).append(rte_interventions_desc).append(rte_interventions_name)
    if (re.match('unknown', rte) and len(set(rte))>1):
        rte = rte.remove('unknown')
        return sort(rte).join('+')



# This function checks if the word in list y appears within the strings in list x

def string_match(list_x,list_y):
    output= ''
    for x in list_x:
        flag = 0
    for y in list_y:
        for re.match(('\\<' + tolower(y) + '\\>'),x.lower()):
        flag =1
        return output.append(True)
    if flag ==0:
        return output.append(False)


# This function uses a fuzzy string matching to map a condition to the icd category



# fuzzy_match < - function(conditions, icd)
# {
#
# # Creating an empty column
# conditions$match < - NA
#
# # Initialize index
# i = 1
#
# # For each condition in the dataset
# for (condition in conditions$condition_polished) {
#
#     # Return all the matches
#     x < - agrep(condition, icd$description, ignore.case = T, value = T, max.distance = 0.1, useBytes = T)
#
# # Count the number of matches (if any)
# len < - length(x)
#
# # If there is at least a match
# if (len > 0) {
#
# # If there is exactly one match
# if (len == 1) {
#
# # Return the match
# conditions$match[i] < - x[1]
#
# } else {
#
# # Return the best match (i.e. the match with the minimum distance)
# dist = adist(condition, x, ignore.case = T, useBytes = T, partial = T)
# conditions$match[i] < - x[which(min(dist) == dist)[1]]
#
# }
# }
#
# # Increment the index
# i = i+1
#
# }
#
# return (conditions)
#
# }
#
# # QUERIES ------------------------------------------------------------------------------------


