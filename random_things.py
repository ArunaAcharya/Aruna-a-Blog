# new_blog= BlogPost(
#     title= "Top 15 Things to do When You are Bored",
#     subtitle= "Top 15 Things to do When You are Bored",
#     date="August 31, 2009",
#     body="Cupcake ipsum dolor. Sit amet marshmallow topping cheesecake muffin. Halvah croissant candy canes bonbon candy. Apple pie jelly beans topping carrot cake danish tart cake cheesecake. Muffin danish chocolate soufflé pastry icing bonbon oat cake. Powder cake jujubes oat cake. Lemon drops tootsie roll marshmallow halvah carrot cake.",
#
#     author="Aruna Acharya",
#     img_url="https://images.unsplash.com/photo-1520350094754-f0fdcac35c1c?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1650&q=80",
# )
# with app.app_context():
#     db.session.add(new_blog)
#     db.session.commit()
# posts = []
# with app.app_context():
#     blog_posts = db.session.query(BlogPost).all()
#     for blog_post in blog_posts:
#         each_post = {
#             "id": blog_post.id,
#             "title": blog_post.title,
#             "subtitle": blog_post.subtitle,
#             "date": blog_post.date,
#             "body": blog_post.body,
#             "author": blog_post.author,
#             "img_url": blog_post.img_url
#         }
#         posts.append(each_post)
#
# with app.app_context():
#     print(BlogPost.query.all())
#