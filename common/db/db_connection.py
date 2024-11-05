# import contextvars
# from functools import wraps
# from sqlalchemy import URL, create_engine
# from sqlalchemy.orm import sessionmaker
#
# from common.util.environment import env
#
# sh_log_engine = create_engine(
#     url=env.get("SQLALCHEMY_LOG_DATABASE_URL"),
#     pool_size=int(env.get("POSTGRESQL_POOL_SIZE")),
#     max_overflow=int(env.get("POSTGRESQL_MAX_OVERFLOW")),
#     pool_recycle=int(env.get("POSTGRESQL_POOL_RECYCLE")),
# )
# sh_log_session_maker = sessionmaker(autocommit=False, autoflush=False, bind=sh_log_engine)
#
# db_session_context = contextvars.ContextVar("db_session", default=None)
#
#
# def transactional(func):
#     """하나의 기능에 대한 transaction의 ACID를 보장한다"""
#
#     # service.py 파일의 함수에 @transactional annotation을 사용함
#     @wraps(func)
#     def wrap_func(*args, **kwargs):
#         db_session = db_session_context.get()
#         if db_session is None:
#             db_session = sh_log_session_maker()
#             db_session_context.set(db_session)
#             try:
#                 result = func(*args, **kwargs)
#                 db_session.commit()
#             except Exception as e:
#                 db_session.rollback()
#                 raise
#             finally:
#                 db_session.close()
#                 db_session_context.set(None)
#         else:
#             return func(*args, **kwargs)
#         return result
#
#     return wrap_func
#
#
# # TODO: session close 부분은 개발, 오류에 on 상태에서 db 수정 안됨
# def repository(func):
#     """ return db session context"""
#
#     # dao.py 파일의 함수에 @repository annotation을 사용함
#     # select, update, delete, 단일건 insert 등 db session을 통해 SQL을 수행하는 경우 활용한다.
#     @wraps(func)
#     def wrap_func(*args, **kwargs):
#         db_session = db_session_context.get()
#         return func(*args, **kwargs, db=db_session)
#
#     return wrap_func
#
#
# def repository_conn(func):
#     """ return engine connection"""
#
#     # dao.py 파일의 함수에 @repository_conn annotation을 사용함
#     # 여러건 insert 할 때 engine connection을 통해 SQL을 수행하는 경우 활용함
#     @wraps(func)
#     def wrap_func(*args, **kwargs):
#         connection = sh_log_engine.connect()
#         return func(*args, **kwargs, connection=connection)
#
#     return wrap_func
