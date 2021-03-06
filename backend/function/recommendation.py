import pandas as pd
import numpy as np
import pprint
from function import helper 

pp = pprint.PrettyPrinter(indent=4)
# ------------------------------------------------------------------
#  Obtain Attribute Weigth 
# ------------------------------------------------------------------
def obtain_attribute_weight(user_pref_attribute_frequency):
    user_pref_attribute_weight_dict = {}
    frequency_sum = sum(user_pref_attribute_frequency.values())
    for attr, value in user_pref_attribute_frequency.items():
        user_pref_attribute_weight_dict[attr] = value/frequency_sum
    # pp.pprint(user_pref_attribute_weight_dict)
    return user_pref_attribute_weight_dict
# ------------------------------------------------------------------
#  Value function
# ------------------------------------------------------------------
def categorical_attributes_value_function(user_pref_v, item_v):
    if item_v in user_pref_v.keys():
        # return user_pref_v[item_v]/sum(user_pref_v.values())
        return 1
    else:
        return 0

def numerical_attributes_value_function(user_pref_v, item_v, attribute):

    # step 1: find the interval that contains the item's attribute value
    value_interval_label = helper.get_numerical_attribute_interval_label(attribute, item_v)


    # step 2: compute the sum of preference value 
    user_pref_v_sum = sum(user_pref_v.values())

    # step 3: probability of preference value
    if user_pref_v[value_interval_label]> 0:
        return user_pref_v[value_interval_label]/user_pref_v_sum
    else:
        return 0
    return 1
# ------------------------------------------------------------------
# Multi-attribute Utility Theory (MAUT) : Get Utility for each items
# ------------------------------------------------------------------


def filter_items_by_user_constraints(user_constraints, item_pool):
    filtered_item_pool = []


    return filtered_item_pool



def compute_recommendation_by_MAUT(user_preference_model, item_pool, top_K, categorical_attributes, numerical_attributes, sort=True):
    # based on user preference model and item value
    # use MAUT to estimate the user's preference for each item

    user_pref_attribute_frequency = user_preference_model['attribute_frequency']
    user_pref_preference_value= user_preference_model['preference_value']

    # item utility
    item_utility_dict = {}

    # compute the attribute weight (normalization)-> the user's attribute preference
    user_pref_attribute_weight_dict = obtain_attribute_weight(user_pref_attribute_frequency)

    # user preference to item w.r.t. each attribute
    user_item_preference_value_dict = {}

    for each_item in item_pool:
        item_id = each_item['id']
        item_utility = 0
        # Step 1: Obtain the value for each attributes
        # 1. Categorical Attributes
        for attr in categorical_attributes:
            user_item_preference_value_dict[attr] = categorical_attributes_value_function(user_pref_preference_value[attr], each_item[attr])
           
        # 2. Numerical Attributes
        for attr in numerical_attributes:
            user_item_preference_value_dict[attr] = numerical_attributes_value_function(user_pref_preference_value[attr], each_item[attr], attr)

        
        # Step 2: Calculate the utility
        # 1. Categorical Attributes
        for attr in categorical_attributes:
            item_utility = item_utility + user_pref_attribute_weight_dict[attr] * user_item_preference_value_dict[attr]
        # 2. Numerical Attributes
        for attr in numerical_attributes:
            item_utility = item_utility + user_pref_attribute_weight_dict[attr] * user_item_preference_value_dict[attr]
        
        item_utility_dict[item_id] = item_utility
    
    if sort:
        sorted_item_utility_list = helper.sort_dict(item_utility_dict)
        # pp.pprint(sorted_item_utility_list)
        top_K_recommmendation_list = sorted_item_utility_list[0:top_K]

        return top_K_recommmendation_list
    else:
        return item_utility_dict


def update_based_on_satisfiability(attr, satisfiability, satisfied_critique_attribute_list, unsatisfied_critique_attribute_list):
    if satisfiability:
        satisfied_critique_attribute_list.append(attr)
        if attr in unsatisfied_critique_attribute_list:
            unsatisfied_critique_attribute_list.remove(attr)
    else:
        if attr not in unsatisfied_critique_attribute_list:
            unsatisfied_critique_attribute_list.append(attr)
    return satisfied_critique_attribute_list, unsatisfied_critique_attribute_list
    
                

def compute_recommendation_compatibility_score(user_critique_preference, item_pool, top_K, categorical_attributes, numerical_attributes, sort=True):
    
    # based on user critique preference and item value
    # calculate the compatibility score for each item

    # item compatibility score
    item_compatibility_score_dict = {}

    for each_item in item_pool:
        item_id = each_item['id']
        item_compatibility_score = 0


        satisfied_critique_attribute_list = []
        unsatisfied_critique_attribute_list = []

        for key, crit_unit in user_critique_preference.items():

            # Step 1: Obtain the value for each critique
            attr = crit_unit['attribute']
            crit_direction = crit_unit['crit_direction']
            value = 0
            if attr in numerical_attributes:
                value = crit_unit['value']

            # Step 2: check the satisfiability
            if attr in satisfied_critique_attribute_list:
                pass
            else:
                # 1. Categorical Attributes
                if attr in categorical_attributes:
                    satisfiability = False
                    if each_item[attr] == crit_direction:
                        satisfiability = True
                    satisfied_critique_attribute_list, unsatisfied_critique_attribute_list = update_based_on_satisfiability\
                        (attr,satisfiability, satisfied_critique_attribute_list, unsatisfied_critique_attribute_list)
                    # print('sat:',satisfied_critique_attribute_list)
                    # print('unsat:',unsatisfied_critique_attribute_list)
                # 2. Numerical Attributes
                if attr in numerical_attributes:
                    satisfiability = False
                    if crit_direction == 'lower':
                        satisfiability = True if each_item[attr] < value else False
                    if crit_direction == 'higher':
                        satisfiability = True if each_item[attr] > value else False
                    if crit_direction == 'similar':
                        item_value_interval_label = helper.get_numerical_attribute_interval_label(attr, each_item[attr])
                        crit_value_interval_label = helper.get_numerical_attribute_interval_label(attr, value)
                        satisfiability = True if item_value_interval_label ==  crit_value_interval_label else False
                    

                    satisfied_critique_attribute_list, unsatisfied_critique_attribute_list = update_based_on_satisfiability\
                        (attr,satisfiability, satisfied_critique_attribute_list, unsatisfied_critique_attribute_list)
                    # print('sat:',satisfied_critique_attribute_list)
                    # print('unsat:',unsatisfied_critique_attribute_list)
     
        if len(satisfied_critique_attribute_list) > 0:
            item_compatibility_score = len(satisfied_critique_attribute_list) / len(satisfied_critique_attribute_list)+len(unsatisfied_critique_attribute_list)
        item_compatibility_score_dict[item_id] = item_compatibility_score
    

    if sort:
        sorted_item_compatibility_score_list = helper.sort_dict(item_compatibility_score_dict)
        top_K_recommmendation_list = sorted_item_compatibility_score_list[0:top_K]
        return top_K_recommmendation_list
    else:
        return item_compatibility_score_dict



def compute_recommendation(user_preference_model, user_critique_preference, item_pool, top_K, categorical_attributes, numerical_attributes, method, alpha=0.5, sort=True):

    if method == 'MAUT':
        top_K_recommmendation_list = compute_recommendation_by_MAUT(user_preference_model, item_pool, top_K, categorical_attributes, numerical_attributes,sort)
        return top_K_recommmendation_list

    if method == 'COMPAT':
        top_K_recommmendation_list = compute_recommendation_compatibility_score(user_critique_preference, item_pool, top_K, categorical_attributes, numerical_attributes, sort)
        return top_K_recommmendation_list

    if method == 'MAUT_COMPAT':
        item_maut_score_dict = compute_recommendation_by_MAUT(user_preference_model, item_pool, len(item_pool), categorical_attributes, numerical_attributes, sort=False )
        item_compatibility_score_dict = compute_recommendation_compatibility_score(user_critique_preference, item_pool, top_K, categorical_attributes, numerical_attributes, sort=False )

        integrated_score_dict = {}
        for item, maut_score in item_maut_score_dict.items():
            integrated_score = alpha * maut_score + (1-alpha) * item_compatibility_score_dict[item]
            integrated_score_dict[item] = integrated_score
        if sort :
            sorted_integrated_score_list = helper.sort_dict(integrated_score_dict)
            top_K_recommmendation_list = sorted_integrated_score_list[0:top_K]
            return top_K_recommmendation_list
        else:
            return integrated_score_dict