import codecs
from dataclasses import dataclass
from lxml import etree as et
from tqdm import tqdm

stanza_str = ""

@dataclass
class Token:
    reference: str
    form: str =""
    lemma: str =""
    snt_id: str =""
    word_id: str =""
    postag: str =""
    head: str =""
    relation: str =""

# made this a method w/fileid for easier testing on shards
def get_history_tokens(fileid):
    if __name__ == "__main__":
        with codecs.open(fileid, "rb", "utf8") as fp:
            xml = fp.read()

        parser = et.XMLParser(encoding="utf-8")
        tree = et.XML(xml,parser=parser)
        tokens = []
        for sentence in tqdm(tree.findall(".//sentence")):
            ref = sentence.get("subdoc")
            for word in sentence.findall(".//word"):
                token = Token(ref, 
                              word.get("form"),
                              word.get("lemma"),
                              sentence.get("id"),
                              word.get("id"),
                              word.get("postag"),
                              word.get("head"),
                              word.get("relation"),)
                tokens.append(token)

        return tokens

# made this a method w/fileid for easier testing on shards
def get_gorman_tokens(fileid):
    if __name__ == "__main__":
        tree = et.parse(fileid)
        tokens = []
        # put tqdm back!
        for sentence in tqdm(tree.findall(".//sentence")):
            ref = sentence.get("subdoc")
            for word in sentence.findall(".//word"):
                token = Token(ref, 
                              word.get("form"),
                              word.get("lemma"),
                              sentence.get("id"),
                              word.get("id"),
                              word.get("postag"),
                              word.get("head"),
                              word.get("relation"),)
                # print(token)
                tokens.append(token)

        return tokens

glaux_tokens = get_history_tokens("0003-001a.xml")
gorman_tokens = get_gorman_tokens("thuc-1-21-40-bu4.xml")
#gorman_tokens.extend(get_gorman_tokens("thuc-1-41-60-bu3.xml"))
# ^ if looking at a sample not captured fully in one of these gormans, this is what I do

#print(gorman_tokens)

#speech_refs = ['1.32.','1.33.','1.34.','1.35.','1.36.','1.37.','1.38.','1.39.','1.40.','1.41.','1.42.','1.43.','1.68.', '1.69.', '1.70.', '1.71.','1.73.','1.74.','1.75.','1.76.','1.77.','1.78.','1.80.','1.81.','1.82.', '1.83.', '1.84.', '1.85.','1.86.','1.120.','1.121.','1.122.','1.123.','1.124.','1.140.','1.141.','1.142.','1.143.','1.144.','2.11.','2.35.','2.36.','2.37.','2.38.','2.39.','2.40.','2.41.','2.42.','2.43.','2.44.','2.45.','2.46.','2.60.','2.61.','2.62.','2.63.','2.64.','3.9.','3.10.','3.11.','3.12.','3.13.','3.14.','3.37.','3.38.','3.39.','3.40.','3.41.','3.42.','3.43.','3.48.','3.53.','3.54.','3.55.','3.56.','3.57.','3.58.','3.59.','3.61.','3.62.','3.63.','3.64.','3.65.','3.66.','3.67.','4.17.','4.18.','4.19.','4.20.','4.59.','4.61.','4.62.','4.63.','4.64.','4.65.','6.9.','6.10.','6.11.','6.12.','6.13.','6.14.','6.16.','6.17.','6.18.','6.20.','6.21.','6.22.','6.23.','6.33.','6.34.','6.36.','6.37.','6.38.','6.39.','6.40.','6.41.','6.76.','6.77.','6.78.','6.79.','6.80.','6.82.', '6.83.', '6.84.', '6.85.','6.86.','6.87.','6.89.','6.90.','6.91.','6.92.']
speech_refs = ['1.32.','1.33.','1.34.','1.35.','1.36.']

speechTokens = {1:[]}
gorman_speech_tokens = {1:[]}

x_bin_list = ['5.1.1']

def deepest_depth(tokens,speech_tokens):
    bin_count = 1
    verb_counter = 0
    first_one = True
    current_sentence = "nil"
    current_ref = "nil"
    tag_suffix = 1
    coll_counts = [0,0,0]
    particle_instances = []

    for t in tqdm(tokens):
        if first_one:
            current_sentence = t.snt_id
            current_ref = t.reference
            first_one = False
        for s in speech_refs:
            if t.reference.startswith(s) == True: 
                if current_sentence != t.snt_id:
                    bin_count = bin_count + 1
                    tag_suffix = tag_suffix + 1
                    if current_ref != t.reference:
                        tag_suffix = 1
                        current_ref = t.reference

                    x_bin_list.append(t.reference+" "+str(tag_suffix))
                    current_sentence = t.snt_id
                    speech_tokens[bin_count] = [t]
                    speech_tokens[bin_count].append(t)
                    #print(t.snt_id)
                else:
                    speech_tokens[bin_count].append(t)
                    verb_counter = verb_counter + 1
                
                # print(t.lemma)
                if t.postag is not None:
                    if t.postag[0] != 'u':
                        coll_counts[0] = coll_counts[0] + 1
                    if t.postag[4] != 'o': 
                        coll_counts[1] = coll_counts[1] + 1
                if t.lemma == 'ἄν':
                    coll_counts[2] = coll_counts[2]+1
                    particle_instances.append(t.head)

    #print("new bin list", x_bin_list)
    ref_counter = 1
    particle_result = 0


    for s in tqdm(speech_tokens):        
        tagged = False

        particle_slice = []

        # grab CO ids
        for w in speech_tokens[s]:
            if w.word_id in particle_instances and "CO" in w.relation:
                particle_slice.append(w.head)
        
        # grab every single relationship
        for w in speech_tokens[s]:
            if tagged is False:
                ref_counter = ref_counter+1
                # print(snt_tag)
                tagged = True

            # grabbing relationship
            if (w.postag is not None) and (w.postag[4] == 'o') and (w.word_id in particle_instances):
                #print("direct: ", w.word_id)
                particle_result = particle_result + 1
            elif (w.word_id in particle_slice) and (w.postag is not None) and (w.postag[4] == 'o'):
                #print("co: ", w.word_id)
                particle_result = particle_result + 1

    coll_result = (2*coll_counts[1]*coll_counts[2])/coll_counts[0]
    print("glaux coll result (expected): ", coll_result)
    print("glaux coll result (found): ", particle_result)
    return

def deepest_gorman_depth(tokens,speech_tokens):
    xx_bin_list = ['5.1.1']
    bin_count = 1
    verb_counter = 0
    first_one = True
    current_sentence = "nil"
    current_ref = "nil"
    tag_suffix = 1
    gor_coll_counts = [0,0,0]
    gorticle_instances = []

    for t in tqdm(tokens):
        if first_one:
            current_ref = t.reference
            current_sentence = t.snt_id
            
            first_one = False
        for s in speech_refs:
            if t.reference.startswith(s) == True: 
                if current_sentence != t.snt_id:
                    bin_count = bin_count + 1
                    tag_suffix = tag_suffix + 1
                    if current_ref != t.reference:
                        tag_suffix = 1
                        current_ref = t.reference

                    xx_bin_list.append(t.reference+" "+str(tag_suffix))
                    current_sentence = t.snt_id
                    speech_tokens[bin_count] = [t]
                    speech_tokens[bin_count].append(t)
                    #print("A", t.snt_id)
                else:
                    speech_tokens[bin_count].append(t)
                    verb_counter = verb_counter + 1
                    #print("B", t.snt_id)
    
                # gorman stuff happens differently, the checks are a bit different here
                if t.postag is not None and len(t.postag) > 0:
                    if t.postag[0] != 'u':
                        gor_coll_counts[0] = gor_coll_counts[0] + 1
                    if t.postag[4] != 'o':
                        gor_coll_counts[1] = gor_coll_counts[1] + 1
                if t.lemma is not None and t.lemma == "ἄν1":
                    gor_coll_counts[2] = gor_coll_counts[2] + 1
                    gorticle_instances.append(t.head)

    ref_counter = 1
    gorticle_result = 0

    for s in tqdm(speech_tokens):
        tagged = False

        gorticle_slice = []

        for w in speech_tokens[s]:
             # print(w)
             if tagged is False:
                snt_tag = xx_bin_list[ref_counter]+" "+str([ww.lemma for ww in speech_tokens[s][1:4]]) # fixed
                ref_counter = ref_counter+1
                # print(snt_tag)
                tagged = True
            
            # grabbing relationship
             if (w.postag is not None) and (len(w.postag) >= 5 ) and (w.postag[4] == 'o') and (w.word_id in gorticle_instances):
                #print("direct: ", w.snt_id, w.word_id)
                gorticle_result = gorticle_result + 1
             elif (w.word_id in gorticle_slice) and (w.postag is not None) and (w.postag[4] == 'o'):
                #print("co: ", w.snt_id, w.word_id)
                gorticle_result = gorticle_result + 1

    # PRINT YOUR COLLOCATION CALCULATION :]
    gor_coll_result = (2*gor_coll_counts[1]*gor_coll_counts[2])/gor_coll_counts[0]
    print("gorman coll result (expected): ", gor_coll_result)
    print("gorman coll result (found): ", gorticle_result)
    return

deepest_depth(glaux_tokens, speechTokens)
deepest_gorman_depth(gorman_tokens, gorman_speech_tokens)
