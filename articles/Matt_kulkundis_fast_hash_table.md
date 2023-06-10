Hello. Welcome, I am Matt Kulukundis. This is "Designing A Fast, Efficient,
Cache-friendly Hash Table, Step by Step". If you thought it was something else,
stay, this is better then what you thought it would be. Trust me. But before I
start, I just wanna give credit, 'cause this is the work of a lot of people. I
am not the primary author of many of this, I'm more the primary evangelist. I
convince people to do things and they listen to me 'cause they're fools. In
alphabetical order, I wanna thank Elcus Evlogimanos, who is probably the most
primary author for all of this. He's done the lion's share of the coding and
much of the deep thought involved. Jeff Dean, from Google, came in with some
brilliant insights at a very opportune moment. Jeffrey Limb, also, well
everyone's at Google. Jeffrey Limb did a bit of the very micro-optimization of
assembly. None of his work is actually gonna be covered 'cause it's way too low
level. Roman Periplitza is responsible for all of the crazy template hackery.
Sam Benza also did a huge volume of the code reviews, the template hackery,
some of the optimization work, and is just sorta generally spread himself
across all of it effectively. Sanjay Ghemawat, came in with Jeff Dean, at the
same moment. Provided a very key observation. If you don't know Sanjay and Jeff
Dean, they're sort of like a single hive mind that walks around in two bodies.
Vitaly Goldstein did a bunch of work around the hash functions and is still
doing it. This is a massive team effort and it would be arrogant of me in the
extreme, more arrogant than I typically present, to not siphon the net. As I
said, we're designing cache tables step-by-step. You've probably seen this sort
of talk before, right? I start with something simple. No no no, this is a talk
in C++. I start with something simple and then I'm just gonna blow past it to
something complicated much faster than you can follow. That's how these talks
work. It's always how step-by-step talks work. I'm sorry, it was in my
contract. Let me give you a few words of warning, though. For the purposes of
this talk, table, map, and set are interchangeable words.

If I had more practice, I would always say table but I'm bad at that and I'm
just gonna throw map and set in there to confuse you, 'cause I like doing that.
What I say, I am aiming for 90% true. Perfect fidelity interferes with
understanding when you are dealing with a topic this complicated. Right? 90%
true. A huge amount of the performance of a hash table depends on the quality
of your hash functions. There are doctoral theses about this, and I'm gonna
gloss over all of it. I'm just gonna assume that we have a good hash function
for whatever definition of good I want. I will try to call out the spots where
it matters the most. But on this sum, and you should just know, you have a good
hash function. The interaction between hash functions and hash tables is very
subtle and often depends on the exact implementation of the table. Little bit
of background, right? Hash tables are incredibly performance sensitive. At
Google, right now, as I am speaking, in our fleet, one percent of the CPU's are
computing something inside a hash table. As I am speaking, more than four
percent of Google's RAM is owned by a hash table, and that's just in C++. I
don't know how to get the numbers for JAVA. At these scales, there is no trade
off. None. That is correct for all users.

When we talk about hash tables, you have to talk about whether a table is cold
or hot. Does the entire table fit in L1 Cache? If it does, then you should be
counting instructions. If everything's in L1 Cache, it's all about how many
instructions are executed. If everything's cold, all you really need to talk
about are L1 Cache misses. Everything else comes for free. As with anything
like this, benchmarks are the only source of truth you will ever get, and they
are lies. Every last one of them. You can find a lot of blog posts about like,
"I made the fasted hash table ever and here's my one benchmark to prove it.".
Anytime someone comes to you with one benchmark, they have gamed that
benchmark. Sorry. Google's a big code base. We talk about it a lot. Trust me,
it's really big. Hyrum's Law, and Titus has told me this slide is obligatory,
is a very real thing at Google.

For those of you that don't know, Hyrum's Law says if there's anything a user
can observe

about the implementation of your API, they will rely upon it, given enough
users. And this is the bane of the janitor's existence. This is the bane of the
CPP Standard's existence.

What can we look at Google's code base and figure out? We're still in the world
of background, sorry. I know there's a lot. Nobody races, except for the people
who do. Only two operations really matter, "insert" and "find".

Except for the people who need efficient table scans. That's just iterating
over the whole table. Nobody uses the bucket interface, I'll define that in a
moment. But nobody, and there's no Hyrum's Law exception here. Literally
nobody. There was one use of it in Google Three and it's a devoed API. Nobody
uses load factor correctly. I audited every user of load factor in Google
Three. They were all wrong. All of them. With that covered, enough mornings and
context, I'm gonna introduce to you the new hash table at Google called Swiss
Table. It is the fastest hash table in the world, with no caveats, ifs, ands,
or buts. It's the best in all situations. Okay, a couple people got that it was
a joke. Let's start with unordered map, unordered set. This is our starting
point. You're gonna see diagrams like this a lot so let me walk you through
what the parts of this diagram are.

The H, that's your hash code. It is 64-bits in all of it's glorious splendor. I
don't care about 32-bit platforms. If you're on a 32-bit platform, whenever I
say 64, make some mental adjustments. It's fine. Technically, this is optional,
but it's usually there so I'm going to include it. This is the actual value.
This is the thing that we want to store. Because the value is in a separate
allocation, we say that it has pointer stability. No matter what happens to the
internals of your hash table, the value doesn't move. This is a property
guaranteed by the standard. That is the symbol for an all-pointer. I know, it's
awesome, isn't it? This is used to indicate the end of length lists.

These values are in the same bucket. I mentioned the Bucket API, right? When
you take the hash, you mod by the table size, and then you end up with a
bucket, and that bucket chain is all of the values that land in that bucket.
Load factor is how many things are in your table versus how many slots you
have, what is your bucket count. For this beautiful table, 60%. Tables use the
load factor to decide when they want to grow.

Back to where we were, this is our starting point. Std::Unordered_set. This is
90% true. I wonder if we can make this a little more true.

Yeah, it really does look like that. And I know you're sitting there going,
"Whoa." but there's a trick to dealing with the standard. You slow down, take a
deep breath, and just lie back and think, "Oh, now it makes sense.". Yeah. That
still's starting to make sense, and that is never a good sign. But this
picture's more true. Oh, I should mention, whenever I'm talking about the
standard, I'm talking about Lb std C++ 4.9? 4.8? Something around there. Yeah,
I know it's old, don't judge me. I don't choose that and upgrading is a pain.
What can we learn from this picture? We store the hash and the pointer. That's
an extra 16-bytes per entry. And I can hear you say, 16-bytes? That's like,
practically free, who cares. Turns out that it's somewhere between .1 and .2%
of fleet-wide RAM at Google.

Did I mention that hash tables are used a lot?

When we iterate across this thing, we actually end up walking this length list.
It's o of size. It's kind of a random thing for me to mention here, we're just
gonna put a pin in that. We'll come back to it later. The iteration order for
this container is reproducible for any given insertion order. Hyrum will rear
his actually fairly attractive head at some point later. But let's look at how
"find" on this table operates in action. We wanna find this element, it happens
to be the second one on our bucket chain. We compute the hash to figure out
where we're going. We follow that to the entry before the first entry in our
bucket chain. So we always just skip this one. Then we look at the first entry
that's actually there. We compare our computed hash against the hash stored in
that thing. If that matches, we compare the value against the value that we
want. And then we skip, because it didn't match, and we get to the one we
actually wanted. Four different memory accesses to find that element. It's
kinda stinky. I'm trying to tone down my language, I'm sorry. I worked on ships
for a while, it has left me with a foul mouth. If a few expletives slip out,
please forgive me.

Back to our simplified view, here we are. But let's improve it just a little
bit with what we learned from our deeper dive. There's a dummy node. Yeah, it's
there. Why is it there? Well, in order to insert into a singly linked list, you
need to have the element before so that you can slice it in appropriately. Now
you could say, why don't we just put it at the end of the singly linked list?
But then you have to iterate to the end of your bucket chain to insert a new
item on that bucket chain, and that was just the thing they decided was an
unacceptable compromise. I didn't design it, I don't know. What could we do
about this? We could make a doubly length list. Then we could insert without
it, we don't need that extra dummy slot, but that adds another eight bytes to
everything. That's another .1% of fleet-wide RAM, and most of the reason I
started this was to save RAM.

Also, it fluffs out our L1 caches, which makes us feel bad about ourselves and
the whole thing sounds expensive so let's not do that. What if we could make
this more like our original picture? What if we just try and return it to our
mental model? This is not an awful idea. It looks simpler. Coincidentally, this
is what gene UCCX hash map actually looks like. What do we gain when we do
this? We eliminate a memory interaction, on "find" and "insert". By the way,
this "what do we gain", "what do we lose"? It's gonna come up a lot. This is
how you need to think when you are optimizing a data structure. What do we
gain? We've lost memory instruction. Indirection. What do we lose? Iteration
requires scanning, not just across our buckets, but across the entire array, so
now iteration is not o of size, it's o of capacity plus o of size. And I can
hear the theoreticians mulling. You're saying, capacity is bounded by max load
factor over two and max load factor, which is a constant and therefore, it's o
of size, and you would be correct, except for the people who reuse their
tables. They grow it out to a million elements because they have some request
that needs a million things, then they call clear and then they insert seven
elements and then they iterate over it. Ask me how I know about these people.
Hyrum's Law strikes again.

On the plus side, these people are the minority. We're kinda willing to lose
them for now. Why aren't we paying for that hash? Maybe we could just drop the
hash out of here, and save ourselves a little bit. Felt good, I feel like I
lost some weight. Do I look thinner? No? Maybe? What did I lose when I did
this? Now when the table resizes, I need to recompute the hash, which is
potentially expensive, 'cause I have to call the hash function on every element
already in the table. But is that expensive? It depends on the type. If it's an
int or a double, no. Actually, computing a hash function is basically free. If
it's a big, complicated type, yeah, it is expensive. It's a trade off. I hear
trade offs are a thing. Now when we're trying to run "find", we might have to
run EQ more often, because we can't fast path out by comparing the hashes. Is
that expensive? It depends on the type. If your quality is expensive to
compute, like a string? It could be expensive. But if your quality is cheap to
compute because it's an int or a double or something, no. And we got rid of a
branch. Trade offs. On the plus side, users can get this back if they want.
They can put in a type that caches it's own hash value. We didn't technically
lose any power. We may have lost some convenience. What did we gain? About .1%
of fleetwide RAM. I know, also the vague feeling of superiority when we force a
difficult decision onto the user. And that is the C++ way. (laughter) Maybe I
can do it again. What if I remove the pointers? What did I just do? This isn't
even a chaining hash table anymore. This is a probing table. This is madness,
or is it? Sure, probing has an entire rich field of academic depth to it, that
we're not gonna go into, but what did we gain? Another .1% of fleetwide RAM.
It's kinda awesome. What did I lose? If I iterate over the buckets for a given
thing, it becomes a lot more complicated. But the good news is, nobody uses the
bucket interface. Literally, nobody. Not even Hyrum. It's amazing. Why don't we
try and see how "find" works. We're looking for the same element again. We'll
do our thing. We compute the hash, we go to the spot. We jump to the first
thing, the value doesn't match. We probe to the next one, and then we found it.
It's worth noting that this probe is free, because it's right next to the first
piece in memory. Our cache fetch pulled it in, no extra cost for that. So here
we are, only three memory accesses, instead of four.

But I hear sorta ciserations of concern. What about erasing elements? Won't
this affect our bucket chain in some way? And the answer is yes. We just add
sentinels. You have a little dead marker that says, this is a tombstone. When
you're probing for a "find" or an "insert", you can't stop just because you
found an empty thing. Well, you can't stop when you find a deleted element. You
have to stop when you find an empty element. And then you might be thinking,
how did tombstones interact with load factor? Cause load factor is trying to
express this concept of how full your table is, which is really just trying to
tell you how long your probe sequences are. And tombstones add to your load
factor, so "erase" doesn't actually free up your load factor. It's kinda
annoying but nobody uses load factor correctly anyway. You might be asking, did
we just break standards compatibility? Yes. Multiple times. This code in the
standard is guaranteed never to trigger a rehash. I'll give you a moment to
read it while I drink some of this lovely, lovely Diet Mountain Dew.

That was a joke for my friends. This code will never trigger a rehash with
std:unordered_set but with our new hash table, it can trigger a rehash,

and I just don't feel bad about it. I've looked in Google. Nobody relies on
this, nobody. It turns out Hyrum isn't quite as right as he thinks but, boy, is
he nearly as right as he thinks. Let's give this guy a name. Node_hash_set. I
like it. It has nodes, it's a hash set, and it also has this sorta weighty,
future portent. Why would I call it node_hash_set if I didn't have some other
thing that could go there? Turns out I read the talk, I know where it's going.

We've gone far enough with that data, and I've been told that all talks need
graphs, and rather than just a giraffe going up and to the right, I'm gonna
include a real one. Before I do that, let me talk about benchmarking. There are
a whole space of benchmarks. You need to know how full is your table. Did it
just grow? Is it at it's minimum occupancy, or it is one element from growing?
Is it at it's maximum occupancy? Or is it somewhere in between? How does the
memory interact with cache? Is your table entirely an L1 cache, just super hot
and ready to go, or is your table so large that it's way out to RAM? It's not
even in your L3 cache. You see it cut off in the distance, you're like, "Bye,
honey." (sighs).

Yeah. What are you doing? If you're doing a "find", did you actually find the
element, or is the element not in the table? If you're doing an "insert", is
the element not in the table, or is the insert succeeding? These are all sorta,
there's a giant space of these things. When we first wrote our benchmarks, the
very first run took three days, and then we looked at that data and
aggressively cut dimensionality. But without running the data once, how do you
know what dimensions are inconsequential? Also, how large is the key that
you're keeping in it? Are you keeping ints in your set? Or are you keeping
massive structs that are a meg each? Please don't keep massive structs that are
a meg each. Or use a node one that has an indirection.

So, and I really need to stop saying "so" on slide transitions. I'm trying to
fix it. I'm sorry, folks. It's a hard habit to break. I can go into a whole ton
of variations on this graph, but it would take a big chunk of time, and really
wouldn't be that illuminating. What is this graph? This is std::unordered_set
vs node_hash_set. We are trying to find elements that are present in the graph,
they are in the set. They are our four byte elements. What's the biggest
takeaway? Two x faster. Whoo, that's awesome. Less RAM. That's also made of
awesome. All the other graphs I would show you for this comparison are
basically the same, and I have to place to be so we're gonna keep going from
here. We have our node_hash_set. We got this far by removing data and
indirections. Now we have a choice. If you take the red pill, we're gonna leave
the standard further behind. We're gonna eliminate more indirections and we're
gonna find all performance we can. If you take the blue pill, we're gonna play
games hiding hash codes in inappropriate places in our pointers, and leave the
space of things that I have data on and start to speculate a lot more heavily.
But before you decide, let me ask you a trick question. What's the first thing
you reach for? A stood vector, or a stood list? Yes, a vector. Why is an
ordered map any different? Like I said, it was a trick question. We put the
values right into it. We took the red pill but what are those. Sentinels. Don't
mind them. I'm sure you have two distinct entries for your value that you're
never gonna need to represent in your map. You just too, and that besides...
Look. Four to five times better. Totally worth those sentinels. Also I cheated.
This hash table exists in the wild. It is called dense_hash_set. You can find
multiple copies of it running around on the internet. Just search for it using
Google. Somebody got the joke. It only has a couple small problems. It's a
little bit old and crufty so you're gonna need to update it to the more modern
API's. It has to have those sentinels in it and it's performance degrades with
the size of its keys.

This is four byte keys versus 64 byte keys. The performance goes down 80
percentish, almost two x. This is not pretty. You have your dense_hash_set
somewhere and it's some value you don't own and somebody over there adds some
entries into that struct, and all of a sudden, your performance falls off a
cliff? That's not a fun trade. We're gonna table the size question for a moment
and think about, maybe we can get rid of the sentinels. 'Cause the sentinels
are the biggest usability issue for dense_hash_set.

Sentinels. I'm gonna need a little bit more space. Give me a moment while I
rearrange. Yeah, much better. Maybe if I add just a little bit of metadata
instead of having sentinels. Everybody loves metadata. So what is this? We're
gonna keep a little parallel array of metadata. Dark secret, it's in the same
allocation but, for purposes of our talk, we can think of them as separate.
What do we need to keep in our metadata array? We need to know whether it's
empty, whether it's full, or whether it's deleted. One and a half bits, that is
slightly awkward.

We could do something where every two elements gets three bits and something,
the bookmarking gets really painful and, I always hear people talk about it and
I've never seen the code for it. I would not ask someone to do that in an
interview so I don't want to do it right now. I kinda wish that someone way
smarter than me would just show up and be like, ooh! A wild Sanjay and Jeff
Dean appear. That was really oddly convenient. What are they saying, in case
you can't see? To use a whole byte, "Use a whole byte for the meta-data for
each element, and store seven bits of hash code in the lowest part of it." You
can do one thing for saying, am I a sentinel? Empty or delete it. Then appears
in the seven bits. Or zero means full and I have seven bits of hash code.

By the way, this totally happened in real life. We were struggling with
problems and Jeff Dean and Sanjay sent me an email out of nowhere.

Now we have a two-level hash table. H1 is 57-bits and it tells us where to look
in our backing array. H1 is what we take the modulist of when we're figuring
out where to go. H2 gives us this little bit mask that has to appear in the
control bytes. This is where your hash function starts to become important. If
your hash function hides all it's entropy in the first seven bits, you're gonna
need a lot of H1 collisions. If your hash function puts none of it's entropy in
the first seven bits, you're gonna get a lot of H2 collisions. And any type of
collision is bad. I'm just gonna say that we need a hash function that
distributes the bits well. I'm gonna leave it at that, let you guys do a little
bit of research on your own later. Such things exist. There's even ways to take
a weak hash function and turn it into a strong hash function.

Things are gonna get complicated really quickly now. We're right at the moment
where the coconut is heading, the machete is heading towards your arm, and
we're hoping it hits the coconut. I'm gonna give a few things names. Position 3
has two notional items. It has a control byte in the metadata and a slot, that
actually stores the value. I know, not that many names. Now let's look at what
we are storing in the control byte. We have our sentinels, all have high bit 1,

and our full things, all have high bit 0. You may ask what that extra kSentinel
is 'cause I only mentioned empty, deleted, and full before. It's the thing that
lets you stop scanning your metadata for a table scan. I'm gonna mention it now
and we're never gonna talk about it again. This never happened. Here's our H1
and our H2. It's kinda obvious, it's not that complicated. What does "find"
look like for this table? Quick show of hands, who wants to read all the code
on this slide? And who wants to see a picture of how it works, and then I'll go
back and let you read the code on the slide? People who want to see a picture?
People who want to read the code? Sorry, coders, pictures have it. Once again,
we're finding the second element in that bucket chain but I'm gonna need to
zoom in 'cause those control bytes are really small. If you're feeling awesome,
you can count them. I made sure that eight of them fit in one of the others.
Here we are, we zoomed in on our control bytes. First thing we do, compute
where we're looking. There we are. Our H2 hash didn't match for this element so
we're gonna keep going. Nope, that one's deleted. Keep going. Hey, third
position in our control bytes matches. H2 anyway. Let's go check our value.
Yes, got it. That's awesome. Two memory accesses, pretty sweet.

Let's find, I'll give you a few minutes, moments, not minutes, to read the
code.

It still does probing but, as you saw, most of the probing happens in the
control bytes. And that means it all happens really dense in L1 cache. We can
handle really large probe chains before we need to fetch another L1 cache line.
Which is kinda awesome. But I wonder if we could do something better. I kinda
wish someone brilliant would just show up and, yeah, I know, it's lame to reuse
the same joke, but it really did happen. Use SSE instructions. Alright, these
two guys are really smart. Let's just try out their idea and see how far this
gets us.

Here's some SSE instructions to give us a BitMask for it. A couple machine
instructions, everyone follows that instantly. Totes. I didn't spend three
weeks with Elcus trying to understand this, you all got this. We'll go into a
little bit. Set1_epi8 will initialize 128-bit vector of 16 8-bit things.

It's just splatting it out again. It's pretty simple. Compare EQ_epi8 takes two
128-bit things and

it gives you masks of zero or FF where the bytes line up.

Also pretty simple. It turns out most assembly instructions are pretty simple.
It's just when you combine them really densely with code with a lot of
underscores, that your eyes start to bleed. You're like, why did I do this?
There we are. Cmpeq_epi8. Movemask_epi8 takes our big 128-bit thing and
squishes it.

Takes the high bit of each byte and gives us a 16-bit thing that has zeroes
where they didn't match and ones where they do match. Also known as a bit mask,
telling us which of our 16 control bytes had the proper H2 hash.

If we put these instructions together, we get this nice thing that says, give
me the H2, give me the bit mask, for every one that matched. It's kinda
awesome, and it's three instructions. You get 16 probe length in three
instructions. It's amazing. Like I said, Sanjay and Jeff Dean are brilliant.

Alright, it's time to name a few more things. You can always tell when things
are about to get complicated because I start naming them. I'm pretty sure
there's a theory in postmodernism about this. Did I hear a vague concern or
cisseration? No, great. I'm gonna call a group of 16 of these things. 16
control bytes and 16 slots is a group, and our table is gonna contain N groups.

It does mean our table will have a size of N times 16, but who cares, you never
really wanted an exact size for your table. What you wanted was that sweet,
sweet performance. Now that I have these names nailed down, let's look at how
"find" is implemented. I'm not gonna poll the audience again. I'm just gonna do
the pictures and then come back to the code. Here we are, we're about to do our
find. Step one, look at all of them in parallel. Step two, jump to the matching
element. It's awesome. It's okay if you're wowed by this, I still am. It really
does, it's crazy. Here we are, looking at "find". I'm gonna let you read the
code for a bit while I drink this sweet, sweet Diet Mountain Dew here.

Now is the moment when we should make some brilliant observations about this
code. This equality operator is almost always true. By the time we've gotten to
this equality operator, we know that H1 modern table size is a match for this
hash code. We know that H2 is a match for this hash code. We've compared a lot
more bits of our hash code then a traditional table would, so this is always
true. And we can just tell our compiler that. Predict true. I didn't put it in
the slide 'cause it gets long, it's ugly, and it's in all caps. Caps scare
people. True story. This branch says whether we need to probe to the next
group.

We only need to prove "probe to the next group" if the entire group of 16
elements is full. And that basically doesn't happen. If you have a perfectly
distributed hash table, which I know doesn't exist, but work with me here. If
you have a perfectly distributed hash table, you have to have a load factor
greater than 94% before this "if" can ever be false.

It's pretty good that way so we can also give the compiler a hint about that
one. "Erase" also gets a little bit of benefit from this fact. Now when you're
erasing an element, if any other element in the group was empty, you don't have
to put a tombstone it. You can just send it back to empty. Which means you
don't need to hurt your load factor, and then all your finds are more likely to
never need that branch. It's just win-win.

I'm still blown away by these things. Let's look at a little bit of graphs. I
know, there are a lot of graphs, because if you don't have only one graph, it's
hard to read. The red is std::unordered_set. Those of you who are colorblind,
that is the top line in all graphs. The blue is dense_hash_set. The green is
our new thing, flat_hash_set. The left column is small payloads. These are four
byte payloads. The right column is 64-byte payloads. The top is when you are
finding an element that is in the table. The bottom is when you are finding an
element that is not in the table.

What conclusions can we draw from this? We are crushing std::unordered_set,
just across the board. It's awesome. We actually crush dense_hash_set most of
the time.

The one exception is if you have four byte items in your dense_hash_set and
you're looking for things that are in your dense_hash_set, it's faster. Just a
little bit.

Turns out when your values are four bytes, the one byte you spend on metadata
for probing is kind of expensive as a ratio of these things, and the fact that
you have reduced probe chains doesn't quite win out over the extra cacheness.

But you'll notice, one of the things this table does really nicely, if your
elements aren't in the set, you don't even go to the values. You stay right in
the metadata. Most of the time.

Now's when the talk takes a slight left turn. For those of you who don't
recognize the reference, this is the Monty Python "and now for something
completely different". Thus far, everything I've explained to you is about
algorithmics, right? How do we get the algorithmic choices for a hash table
better? Certainly some of them are just by constant factors, but they're still
algorithmic choices. Let's think about ergonomics of our containers for a
moment. And don't worry, std::unordered_map was built with all the loving care
of std::vector_full.

Std::vector_full, we all knew it. I'm gonna show you some code. We're gonna
play a little game. People just throw up a hand when they realize what bear
trap they're standing in.

We got the fast person. I like that. But I'm gonna wait just a little bit more,
oh, I see a few more popping up. Yep, that's right. You're const char star key
is being created as a tenth string in that "find" call. It is, of course, two x
slower. Heterogeneous lookup would fix this but std::unordered_set and map
don't get heterogeneous lookup. They do for our containers because we love the
user.

This one is a little bit harder though someone at a talk I was at earlier
actually identified it.

That is the fastest anyone has gotten this. I had to get Elcus to explain this
one to me over ten minutes on IM. It turns out that because you don't have a
const on your "p", your insert is going to be a ref ref overload, and not the
const ref overload, and thus you are making a copy when you thought you were
doing all the right things.

It's C++. Really (sighs)?

How 'bout this one? Anyone see what they did wrong this time?

Yup. Naturally, calling "emplace" will new a node on the heap, then try and do
the "emplace" and realize, oh I already have this in the container, and then
free that node from the keep for you. Yeah, and don't forget the const down
here, or you're back in the previous bear trap. These are all variants on a
theme. It turns out, we can avoid constructing these temporary objects if we do
something reasonably clever with template. It turns out we can and the answer
is-- it's simple enough to fit on one slide. (laughter) It doesn't fit well and
it kinda makes my brain hurt. This little trick allows us to avoid a ton of
extra copies, and some common pitfalls. Roughly, what this bit of magic does is
it grovels through the arguments you were passed, and it tries really hard to
see their true nature. Once it has seen the platonic ideal of the arguments
that you have passed, it uses that to look at the hash code, instead of being
like, well man, he asked to emplace so I gotta allocate a node right now and
then grovel through it. It does work. Please don't ask me how. Roman is the
person you need to ask how. Fortunately, he's not here.

We're switching a little bit. This one is a little bit harder. You're gonna
need to know some of the internals of dense_hash_map. Your first hint, anyone
want a hint, or do you want to keep staring?

Alright, your first hint is that it is a probing table. It is dense_hash_set.
Your second hint is that std::hash for an int is an identity. Does anyone see
it now? Remember when I talked about low order bits and entropy? We're shifting
left by ten bits so everything has the same low order bits in it's hash code.

And it's 25 times slower. All you need to do to fix it is to give it a better
hash function.

We made that a little better for you. We provide a better hash function by
default. You're welcome.

I had to watch Moana on the way to the plane here. Had I actually done that, I
totally would have put the "You're Welcome" there. Retrospect, whomp whomp.

These things are all subtle. They interact really deeply with each other. The
power of defaults is massive. We're not gonna give you a button to blowup the
world on the first attempt. I mean, you can do it in more advanced attempts but
we try really hard to make it, to give you affordances that make these things
usable. We've even begun migrating, rolling out these across all of Google. We
are sending changes to everybody's code in Google. It's like, hey, you got an
unordered set. Switch you to this one. It's pretty awesome. What are we looking
at? This is a percentage of fleetwide CPU that is consumed by hash tables. This
is a stacked graph so what you want is, you want to notice that we're going
down and to the right. That means we are using less fleetwide CPU. It's about
half a percent of fleetwide CPU has gone down from these migrations. And this
is our live sampling profiler in PROD. This is God's truth as near as we can
tell it. If you're wondering about the colors, the blue is std::unordered_set.
The red is dense_hash_set. The yellow is our new hash tables, and the green is
gene UCXX hash map. But the thing to note is we're trying to replace them all,
and we're getting some good wins in CPU. We're getting even better winds in
performance. I should warn you, the axis changed. This was 2.4 at the top. This
is six at the top. We are saving little over one percent. Ballpark one percent
of fleetwide RAM. These numbers are really big when you multiply it by the size
of Google.

I can hear the crowd murmuring to me like, wait, you're doing a rollout but
you've also said that there are experiments in the works. How are you doing
this without Hyrum coming and beating down your door? You can't make substance
of changes. Hyrum will stop you. The answer is careful defense. Anyone guess
what this returns?

Close, yeah. Our hash seed has a little mix step in it. In debug, we actually
see that hash with random thing. In non-debug, we use address layout
randomization to give us just a little bit of randomness. And that shift by 12,
that's 'cause we found out it works better. I've done some things I ain't proud
of, and the things I am proud of is frankly disgusting.

But it gives us randomization on our tables, and then we figure out where to
insert an element in the group, in debug, mod 13 over six, or mod 13 is greater
than six.

It's a kinda cute way to be like, flip a coin for me. I mean, it's almost a
coin. So it's true 50.3% of the time. Pretty sure somebody is going to start
using flat_hash_set to generate random bits. And then they're gonna complain
when I change the distribution. They were like, I was relying on that 50.3.
Come on.

I'm sure some of you are wondering, I read the program description and it said
Swiss table, but he hasn't said Swiss table more than once. Why is it called
Swiss table? I don't understand. The answer is the primary developer, Elcus and
Roman, are in the Zurich office. Closed hashing, abbreviated "ch", is also the
top level demand for Switzerland. And Swiss efficiency has just a good spot in
the zeitgeist.

But, in the end, we decided to name it something more descriptive. But we still
use the codename. There's that. Now I'm going to describe a few of the
experiments that are actually ongoing with this. Our first experiment is
instead of having our groups aligned at 16 boundaries, what if any offset into
your thing can start a group?

What does this get you? It gets you better probing. You have sorta more
different windows you can probe in. It actually gets you better randomization.
This will make the ASLR step of the randomization randomize your tables better
in opt mode, too. People love it when I do that, too. What does it require?
What's the cons of this? Now I need to have 16 elements at the end of my
metadata that are the same as my 16 elements at the beginning of my metadata. I
have to set those things in both places so that if I land in the second to last
spot, I can scan 16 elements forward. Now, "insert" requires us to write two
control bytes in some cases. But what does it give us? It lets us raise the
default max load factor from seven eighths to fifteen sixteenths.

And that is a lot of RAM. And we can raise the max load factor and be faster.
It's amazing. This experiment is probably going to land, I wouldn't be
surprised if Sam landed it while I was talking, just to spite me. This was a
really fun experiment. It's kind of a failure in some way, but I can't resist
showing it because whenever I saw it, I was just, like, (explosion). We're
gonna get rid of the concept of 16-sized groups, and we're gonna have
seven-sized groups. And instead of all the metadata being at the front, all the
metadata is gonna be attached to the front of the group. We have seven
pointers. Each pointer is gonna be eight-bytes. And that gives us eight more
bytes for our metadata at the front of it. Of those, seven of those bytes are
gonna be for eight-bit hash codes. We're now storing an eight-bit H2, instead
of a seven-bit H2. Which is nice 'cause it nudges us toward better things.

We now have one byte left over that's not storing hash codes. Of those, seven
of the bits in it will represent whether an entry is there or not. And finally,
the last bit will tell us, has this group ever been full? Because that is the
only question you need to know whether you should probe to the next group. And
if you add those up, it's 64-bytes. And the hardware people in the room will
think, oh man. That's a L1 cache line. This is really brilliant. And it is. And
if you have eight-byte values, it is very slightly faster. But most of the time
you don't have eight-byte values, and the cost of specializing both of them was
a lot of code complexity that we didn't want to embrace. But if I were
implementing a Python interpreter, or a core hash table in any kind of
interpreted language that always forced me to have an indirection, that would
be my go-to.

Questions? Please use the mics. If you don't use the mic, and you aim a
soliloquy at me, I have to repeat the soliloquy, and rather than do that, I'm
just gonna summarize it in the worst possible light for you.

(applause)

Don't be shy, I can take it.

- [Audience Member] One obvious question is are you guys planning to open
  source it in the near future? I hear Abseil's a thing. I'd keep my eye on
  Abseil. We're not gonna commit to a timeline but if I were a betting man, I
  would put money on before the end of the year.
- [Audience Member] Before the end of the year, cool. Because recently, I was
  trying to use Google Dense Maps. It is still outperforming the unordered map
  from West Hill most of the time, and the key size is small and-- Yeah. And
  doing mostly look-ups. In the get-up of the unordered map, go to Google Dense
  Map, I saw some issues which are not fixed so, does next question is, are you
  guys supporting this Google Dense Map now, or how reliable it is to use in
  the big projects? The existing dense_hash_set and dense_hash_map, as it
  exists right now, is reliable. Many production services at Google use it. Are
  we supporting it? No. We can't be bothered. It's old and crufty. We have this
  new thing, we like it better.
- [Audience Member] Okay, but, you are using the same dense map we're using at
  GitHub right now? There's an open source. Similar. Similar, okay, thank you.
- [Audience Member] What is the resizing strategy of the table as a whole, and
  how do the modular operation with unknown size? Or is it known? The table
  grows, the table grows when it goes above it's max load factor, because no
  one knows how to use max load factor correctly, the set max load factor
  method is a no-op. You're welcome. The table is a power of two size. We are
  experimenting with other sizes with fast modulists but power of two is really
  nice,

because it lets you just do a bit mask to get the lowest bits. It's bad because
if your hash function isn't good, like if your hash function hides all your
entropy in the high bits, that bit mask comes by and hurts you. We're also
experimenting with doing the thing in the table to strengthen weak hash
functions to make them strong. But that is a few extra instructions so it's a
trade off. I hear trade offs are a thing.

- [Audience Member] I just wanted to ask from, I already know from how many
  elements in the set is your map more effective than just the linear
  searching? Like, say for, Yeah.
- [Audience Member] Four-byte values. I don't know offhand. I know that because
  we do the full 16-byte scan in one assembly instructions, it's very
  competitive for most things. But if you just happen to know that, I have a
  vector of three four-byte values, just like use an array and scan them. At
  Google, we have a thing called flat_set or flat_map, which is just, it's
  backed by a vector that's flat.
- [Audience Member] I see.
- [Audience Member] I just wanted to point out that, regarding the bits of
  entropy, you can actually use some type traits to abstract that. Rather than
  rely on fixed number, you just use the traits to give you that. You can. It
  is complicated when you add the type traits to it. Then you say to tell you
  people, your hasher function has to have this thing in a magical place, and
  it's a little bit annoying but yes. You can, it is one of the options we're
  exploring, but because the performance effect of getting your hash function
  wrong is so deleterious, it's often on the order of 30 times. We are leaning
  towards, we will make your hash good.

It's a little bit of the ergonomics on it.

There's no way this talk was so good, nobody else has questions.

(Audience member asks question) Ah yes, the clever man in the front row has
observed that I will not talk about the elephant in the room.

- [Audience Member] I think earlier, unless I misheard you, you said something
  about Google Two and Google Three, what the heck is that? Sorry, Google's
  source control has gone through some historical revisions. There was once
  upon a time, it was SVN, and then it was Perforce, and then there's this
  in-house thing that we use, and we call it Google Three. It's just the third
  iteration of our source control system. It is the monorepo. All the times you
  hear other Google engineers talk about our monorepo with millions of lines of
  code, inside Google, we just call it Google Three.

- [Audience Member] You were suggesting that there might be another solution
  for if you have a heavy delete load, as well? Are you going to be giving
  examples of how to do that, too, or? It is reasonably fast if you have a
  heavy delete load. It's not the very first thing we've optimized for. Our
  sorta rough priorities are "find", then "insert", and then "erase". If you
  pull in your giant thing, and put in a million elements once 'cause your
  query is large, and then you clear it and try and reuse it, on our clear
  call, we won't actually keep that full million elements. We will drop you
  down to 128 elements on the first clear, because otherwise your table scan
  might go to hell. If you're like, no, I really wanted those million elements,
  you can call dot erase begin end, that's your back door.

- [Audience Member] I was wondering if you guys benchmarked against anything
  else because I mean standard unordered maps sort of been known to be slow for
  many years now, and the benchmarks only showed against your own previous hash
  table. Any other implementations? I mean, Robin Hood hashing is super, super
  popular now in new hash tables. We actually did implement a Robin Hood hash
  on top of the same thing, and it turns out all of the extra logic around is
  more expensive. The whole raison d'etre of Robin Hood hashing is we can
  reduce the length of probe chains. But if you can scan a longer probe chain
  for free, it doesn't matter. And so the cost of more metadata to count your
  offsets and to bump things back turns out to be a loss on Robin Hood hashing.
  You'll also find a lot of blog posts about people who've written the fastest
  hash table in the world, and it turns out the difference between how much
  code you need to implement in order to get a benchmark and how much code you
  need to implement to have a useful map is way different.

We got the benchmarks, and then we spent months filling out the tables, and
adding enough tests, and all of that stuff.

The short answer is, yeah, we did some experiments. We did our own Robin Hood
hash. It is possible around Robin Hood hash had performance bugs we didn't
notice but even in our experiments, the Robin Hood hash we had was comparable,
sometimes slower, sometimes faster than the existing dense hash set.

- [Audience Member] You mentioned that you had some ASM tricks, as well. Were
  they beyond the intrinsics or? No, just the intrins-- What Jeff Limb's
  contributions were. There were those sorts of tricks. Much of it was Jeff
  Limb would look at the generated assembly, look at the code, look at the
  generated assembly, think real hard, tweak the code until it generated the
  assembly he wanted.

- [Audience Member] You've used SSE on X-86. What can you say about other
  platforms which doesn't have SSE? It does support all platforms. On non-SSE
  platforms, we emulate these SSE instructions

by using arithmetic on longs. They produce more false positives but they are
still correct. Your group size goes from 16 to eight, 'cause you don't have
128-bit things. You have 64-bit things. But it does work. Chrome and Android
have both expressed a great deal of interest in picking this up. The only
modern CPU's that don't have SSE instructions are actually just old phones.

- [Audience Member] Could you repeat that const pair problem? I didn't quite
  pick that up. That's fair. There are two overloads for "insert", one of which
  will take a const pair const key, value reference, and one of which will take
  an "R value" reference. If you hand it the local that is not const,

you will end up in the "R value" reference overload. With a temporary being
created. It's, you might call it a bug in the standard. I would call it C++
loves you.

I'm told the session is over. (applause)