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
    def new_question(cls, user_id):
        q = cls()
        q.id = cls.get_new_id()
        q.owner = user_id
        return q
    
    @classmethod
    def active(cls):
        return [cls.get(m) for m in r.smembers('%s_active' % namespace)]
    
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
        q.owner = r.get("%s:owner" % id)

        return q

    @classmethod
    def get_new_id(cls):
        id = r.incr("%s_id_gen" % namespace)
        return "%s:%d" % (namespace, id)

    def can_delete(self, owner):
        if self.owner != owner:
            return False

        if self.votes() > 0:
            return False

        return True

    def delete(self):
        r.srem("%s_active" % namespace, self.id)

    def save(self):
        r.set("%s:question" % self.id, self.question)
        r.set("%s:asker" % self.id, self.asker)
        r.set("%s:owner" % self.id, self.owner)

        r.sadd("%s_all" % namespace, self.id)
        r.sadd("%s_active" % namespace, self.id)

    def votes(self):
        return r.scard("%s:votes" % self.id)

    def vote_toggle(self, user_id):
        if self.owner == user_id:
            return

        k = "%s:votes" % self.id
        removed = r.srem(k, user_id)
        if removed < 1:
            r.sadd(k, user_id)

def main():
    for q in Question.all():
        print(q.id)
        print(q)

if __name__ == "__main__":
    main()