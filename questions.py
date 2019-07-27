import redis
import pprint

r = redis.StrictRedis(
    host='localhost', 
    port=6379, 
    db=0, 
    charset="utf-8", 
    decode_responses=True
    )
namespace = "voting"

class Question:
    @classmethod
    def new_question(cls):
        q = cls()
        q.id = cls.get_new_id()
        return q
    
    @classmethod
    def active(cls):
        for m in r.smembers('%s_active' % namespace):
            yield cls.get(m)
    
    @classmethod
    def all(cls):
       for m in r.smembers('%s_all' % namespace):
            yield cls.get(m) 

    @classmethod
    def get(cls, id):
        q = cls()
        q.id = id
        q.question = r.get("%s:question" % id)
        q.asker = r.get("%s:asker" % id)
        q.votes = r.get("%s:votes" % id)
        return q

    @classmethod
    def get_new_id(cls):
        id = r.incr("%s_id_gen" % namespace)
        return "%s:%d" % (namespace, id)

    def save(self):
        r.set("%s:question" % self.id, self.question)
        r.set("%s:asker" % self.id, self.asker)
        r.incr("%s:votes" % self.id)

        r.sadd("%s_all" % namespace, self.id)
        r.sadd("%s_active" % namespace, self.id)

    def vote_for(self):
        r.incr("%s:votes" % self.id) 

def main():
    for q in Question.all():
        print(q.id)
        print(q)

if __name__ == "__main__":
    main()