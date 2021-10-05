""" CSC108 Assignment 3: Club Recommendations - Starter code."""
from typing import List, Tuple, Dict, TextIO


# Sample Data (Used by Doctring examples)

P2F = {'Jesse Katsopolis': ['Danny R Tanner', 'Joey Gladstone',
                            'Rebecca Donaldson-Katsopolis'],
       'Rebecca Donaldson-Katsopolis': ['Kimmy Gibbler'],
       'Stephanie J Tanner': ['Michelle Tanner', 'Kimmy Gibbler'],
       'Danny R Tanner': ['Jesse Katsopolis', 'DJ Tanner-Fuller',
                          'Joey Gladstone']}

P2C = {'Michelle Tanner': ['Comet Club'],
       'Danny R Tanner': ['Parent Council'],
       'Kimmy Gibbler': ['Rock N Rollers', 'Smash Club'],
       'Jesse Katsopolis': ['Parent Council', 'Rock N Rollers'],
       'Joey Gladstone': ['Comics R Us', 'Parent Council']}


# Helper functions 

def update_dict(key: str, value: str,
                key_to_values: Dict[str, List[str]]) -> None:
    """Update key_to_values with key/value. If key is in key_to_values,
    and value is not already in the list associated with key,
    append value to the list. Otherwise, add the pair key/[value] to
    key_to_values.

    >>> d = {'1': ['a', 'b']}
    >>> update_dict('2', 'c', d)
    >>> d == {'1': ['a', 'b'], '2': ['c']}
    True
    >>> update_dict('1', 'c', d)
    >>> d == {'1': ['a', 'b', 'c'], '2': ['c']}
    True
    >>> update_dict('1', 'c', d)
    >>> d == {'1': ['a', 'b', 'c'], '2': ['c']}
    True
    """

    if key not in key_to_values:
        key_to_values[key] = []
        
    if value not in key_to_values[key]:
        key_to_values[key].append(value)


def load_profiles(profiles_file: TextIO) -> Tuple[Dict[str, List[str]],
                                                  Dict[str, List[str]]]:
    """Return a two-item tuple containing a "person to friends" dictionary
    and a "person_to_clubs" dictionary with the data from profiles_file.

    NOTE: Functions (including helper functions) that have a parameter of type
          TextIO do not need docstring examples.
    """
    
    line = profiles_file.readline()
    p2f = {}
    p2c = {}
    current = line.strip()
    if line:
        line = profiles_file.readline()
    
    while line:
        
        if line.strip():
            
            if "," in current:
                current = current.split(",")
                current = current[1].strip() + " " + current[0]
            
            if "," in line:
                line = line.strip()
                line = line.split(',')
                line = line[1] + " " + line[0]
                if current in p2f:
                    p2f[current] += [line.strip()]
                else:
                    p2f[current] = [line.strip()]
            else:
                if current in p2c:
                    p2c[current] += [line.strip()]
                else:
                    p2c[current] = [line.strip()]
                    
            line = profiles_file.readline()
            
        else:
            line = profiles_file.readline()
            current = line.strip()
            line = profiles_file.readline()
        
    profiles = (p2f, p2c) 
    return profiles
        

def get_average_club_count(person_to_clubs: Dict[str, List[str]]) -> float:
    """Return the average number of clubs that a person in person_to_clubs
    belongs to.

    >>> get_average_club_count(P2C)
    1.6
    """
    club_count = []
    for person in person_to_clubs: 
        for club in person_to_clubs[person]: 
            club_count.append(club)
    if len(person_to_clubs) != 0:      
        return len(club_count) / len(person_to_clubs)
    else: 
        return 0.0


def get_last_to_first(
        person_to_friends: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Return a "last name to first name(s)" dictionary with the people from the
    "person to friends" dictionary person_to_friends.

    >>> get_last_to_first(P2F) == {
    ...    'Katsopolis': ['Jesse'],
    ...    'Tanner': ['Danny R', 'Michelle', 'Stephanie J'],
    ...    'Gladstone': ['Joey'],
    ...    'Donaldson-Katsopolis': ['Rebecca'],
    ...    'Gibbler': ['Kimmy'],
    ...    'Tanner-Fuller': ['DJ']}
    True
    """
    l2f = {}
    i = 0
    for name in person_to_friends: 
        full_name = name.rsplit(' ', 1)
        last = full_name[-1]
        first = [full_name[0]]
        update_dict(last, first[0], l2f)
              
        for friend in person_to_friends[name]:
            full_name = friend.rsplit(' ', 1)
            last = full_name[-1]
            first = [full_name[0]]
            update_dict(last, first[0], l2f)
    
    for name in l2f: 
        l2f[name].sort()
        
    return l2f


def invert_and_sort(key_to_value: Dict[object, object]) -> Dict[object, list]:
    """Return key_to_value inverted so that each key is a value (for
    non-list values) or an item from an iterable value, and each value
    is a list of the corresponding keys from key_to_value.  The value
    lists in the returned dict are sorted.

    >>> invert_and_sort(P2C) == {
    ...  'Comet Club': ['Michelle Tanner'],
    ...  'Parent Council': ['Danny R Tanner', 'Jesse Katsopolis',
    ...                     'Joey Gladstone'],
    ...  'Rock N Rollers': ['Jesse Katsopolis', 'Kimmy Gibbler'],
    ...  'Comics R Us': ['Joey Gladstone'],
    ...  'Smash Club': ['Kimmy Gibbler']}
    True
    """ 
    
    inverted = {}
    
    for name in key_to_value:
        i = 0
        if type(key_to_value[name]) == list:
            for club in key_to_value[name]:
                club = key_to_value[name][i]
                update_dict(club, name, inverted)
                i += 1
        else: 
            update_dict(key_to_value[name], name, inverted)
            
    for name in inverted: 
        inverted[name].sort()
    
    return inverted

def get_clubs_of_friends(person_to_friends: Dict[str, List[str]],
                         person_to_clubs: Dict[str, List[str]],
                         person: str) -> List[str]:
    """Return a list, sorted in alphabetical order, of the clubs in
    person_to_clubs that person's friends from person_to_friends
    belong to, excluding the clubs that person belongs to.  Each club
    appears in the returned list once per each of the person's friends
    who belong to it.

    >>> get_clubs_of_friends(P2F, P2C, 'Danny R Tanner')
    ['Comics R Us', 'Rock N Rollers']
    """
    friend_clubs = [] 
    club = 0
    for friend in person_to_friends[person]: 
        if friend in person_to_clubs: 
            for club in range(len(person_to_clubs[friend])):
                if person not in person_to_clubs: 
                    friend_clubs.append(person_to_clubs[friend][club])
                    club += 1                
                elif (person_to_clubs[friend][club] not in 
                      person_to_clubs[person]):
                    friend_clubs.append(person_to_clubs[friend][club])
                    club += 1 
                
                else: 
                    club += 1
                    
    friend_clubs.sort()
    
    return friend_clubs  

def recommend_clubs(
        person_to_friends: Dict[str, List[str]],
        person_to_clubs: Dict[str, List[str]],
        person: str,) -> List[Tuple[str, int]]:
    """Return a list of club recommendations for person based on the
    "person to friends" dictionary person_to_friends and the "person
    to clubs" dictionary person_to_clubs using the specified
    recommendation system.

    >>> recommend_clubs(P2F, P2C, 'Stephanie J Tanner',)
    [('Comet Club', 1), ('Rock N Rollers', 1), ('Smash Club', 1)]
    """
                
    p2f = person_to_friends
    p2c = person_to_clubs
    c2p = invert_and_sort(person_to_clubs)
    results = {}
    if person not in p2c: 
        if person not in p2f:
            return results
        else:
            friend_clubs = get_clubs_of_friends(p2f, p2c, person)
            for club in friend_clubs: 
                if club in results: 
                    results[club] += 1
                else: 
                    results[club] = 1  
    elif person in p2c and person in p2f:
        friend_clubs = get_clubs_of_friends(p2f, p2c, person)
        for club in friend_clubs: 
            if club in results: 
                results[club] += 1
            else: 
                results[club] = 1 
        clubs = p2c[person]
        for club in clubs:
            club_members = c2p[club]
            for member in club_members:
                m_clubs = p2c[member]
                for m_club in m_clubs: 
                    if person not in c2p[m_club]:
                        if m_club in results:
                            results[m_club] += 1
                        else: 
                            results[m_club] = 1 
    else: 
        clubs = p2c[person]
        for club in clubs:
            club_members = c2p[club]
            for member in club_members:
                m_clubs = p2c[member]
                for m_club in m_clubs: 
                    if person not in c2p[m_club]:
                        if m_club in results:
                            results[m_club] += 1
                        else: 
                            results[m_club] = 1 
                                   
    return dict_to_tup(results)

def dict_to_tup(dictionary: Dict[str, int]) -> List[Tuple[str, int]]:
    """Returns a list of tuples of strings and ints from a dict dictionary
    >>> dict_to_tup({'hi': 1, 'hello': 2})
    [('hi', 1), ('hello', 2)]
    """
    recommendations = []
    for key in dictionary: 
        recommendations.append((key, dictionary[key]))
    return recommendations
        

if __name__ == '__main__':
    pass

    # If you add any function calls for testing, put them here.
    # Make sure they are indented, so they are within the if statement body.
    # That includes all calls on print, open, and doctest.

    # import doctest
    # doctest.testmod()
