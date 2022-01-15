from typing import List
from flask import Blueprint

from anubis.models import (
    db,
    User,
    Course,
    InCourse,
    ForumPost,
    ForumCategory,
    ForumPostInCategory,
    ForumPostUpvote,
    ForumPostComment,
    ForumPostViewed,
)
from anubis.utils.auth.http import require_user
from anubis.utils.auth.user import current_user
from anubis.utils.http.decorators import json_response, json_endpoint, load_from_id
from anubis.utils.http import req_assert, success_response, error_response
from anubis.utils.auth.user import verify_in_course
from anubis.lms.forum import (
    get_post_comments,
    verify_post,
    verify_post_owner,
    verify_post_comment,
    verify_post_comment_owner,
)

forums_ = Blueprint("public-forums", __name__, url_prefix="/public/forums")


@forums_.get('/course/<string:course_id>')
@require_user()
@json_response
def public_get_forum_course(course_id: str):
    course: Course = verify_in_course(course_id)

    posts: List[ForumPost] = ForumPost.query.filter(
        ForumPost.course_id == course.id,
        ForumPost.visible_to_students == True,
    ).order_by(ForumPost.created.desc()).all()

    return success_response({
        'posts': [
            post.meta_data for post in posts
        ]
    })


@forums_.get('/post/<string:id>')
@require_user()
@load_from_id(ForumPost)
@json_response
def public_get_forum_post(post: ForumPost):
    verify_in_course(post.course_id)

    post.seen_count += 1

    viewed: ForumPostViewed = ForumPostViewed.query.filter(
        ForumPostViewed.post_id == post.id,
        ForumPostViewed.owner_id == current_user.id,
    ).first()
    if viewed is None:
        viewed = ForumPostViewed(
            post_id=post.id,
            owner_id=current_user.id,
        )
        db.session.add(viewed)

    db.session.commit()

    return success_response({
        'post': post.data,
    })


@forums_.post('/post')
@require_user()
@json_endpoint([
    ('course_id', str),
    ('title', str),
    ('content', str),
    ('visible_to_students', bool),
    ('anonymous', bool),
])
def public_post_forum_post(
    course_id: str,
    title: str,
    content: str,
    visible_to_students: bool,
    anonymous: bool,
):
    course = verify_in_course(course_id)

    post = ForumPost(
        owner_id=current_user.id,
        course_id=course.id,
        visible_to_students=visible_to_students,
        pinned=False,
        anonymous=anonymous,
        seen_count=0,
        title=title,
        content=content,
    )
    db.session.add(post)
    db.session.commit()

    return success_response({
        'post': post.data,
        'status': 'Posted',
    })


@forums_.patch('/post/<string:post_id>')
@require_user()
@json_endpoint([
    ('title', str),
    ('content', str),
    ('visible_to_students', bool),
    ('anonymous', bool),
])
def public_patch_forum_post(
    post_id: str,
    title: str,
    content: str,
    visible_to_students: bool,
    anonymous: bool,
):
    post = verify_post_owner(post_id)

    post.title = title
    post.content = content
    post.visible_to_students = visible_to_students
    post.anonymous = anonymous

    db.session.add(post)
    db.session.commit()

    return success_response({
        'post': post.data,
        'status': 'Post updated',
    })


@forums_.delete('/post/<string:post_id>')
@require_user()
@json_response
def public_delete_forum_post(post_id: str):
    post: ForumPost = verify_post_owner(post_id)

    db.session.delete(post)
    db.session.commit()

    return success_response({
        'status': 'Post deleted',
        'variant': 'warning'
    })


@forums_.get('/comment/<string:id>')
@require_user()
@load_from_id(ForumPostComment)
@json_response
def public_get_forum_comment(comment: ForumPostComment):
    verify_in_course(comment.post.course_id)
    return success_response({'comment': comment.data, 'post': comment.post.meta_data})


@forums_.post('/post/<string:post_id>/comment')
@forums_.post('/post/<string:post_id>/comment/<string:before_id>')
@require_user()
@json_endpoint([
    ('post_id', str),
    ('content', str),
    ('anonymous', bool),
])
def public_post_forum_post_comment(
    post_id: str,
    content: str,
    anonymous: bool,
    before_id: str = None
):
    post: ForumPost = verify_post(post_id)
    verify_in_course(post.course_id)

    comment = ForumPostComment(
        owner_id=current_user.id,
        post_id=post.id,
        next_id=None,
        anonymous=anonymous,
        content=content,
    )
    db.session.add(comment)
    db.session.commit()

    if before_id is not None:
        before_comment: ForumPostComment = verify_post_comment(before_id)
        before_comment.next_id = comment.id
        db.session.commit()

    return success_response({
        'post': post.data,
        'comment': comment.data,
        'status': 'Comment posted',
    })


@forums_.patch('/post/comment/<string:comment_id>')
@require_user()
@json_endpoint([
    ('content', str),
    ('anonymous', bool),
])
def public_patch_forum_post_comment(
    comment_id: str,
    content: str,
    anonymous: bool,
):
    comment: ForumPostComment = verify_post_comment_owner(comment_id)

    comment.content = content
    comment.anonymous = anonymous

    db.session.add(comment)
    db.session.commit()

    return success_response({
        'comment': comment.data,
        'status': 'Comment updated',
    })


@forums_.delete('/post/comment/<string:comment_id>')
@require_user()
@json_response
def public_delete_forum_post_comment(comment_id: str):
    comment: ForumPostComment = verify_post_comment_owner(comment_id)

    db.session.delete(comment)
    db.session.commit()

    return success_response({
        'status': 'Comment deleted',
        'variant': 'warning'
    })


