# users/views.py
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import LoginSerializer, UserSerializer
from django.contrib.auth import get_user_model
from django.db import models
from .models import College, Class, ClassBinding

User = get_user_model()

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'code': 200,
                'message': 'success',
                'data': {
                    'token': token.key,
                    'user_id': user.id,
                    'school_id': user.school_id,
                    'name': user.name,
                    'user_type': user.user_type,
                    'college': user.college.name if user.college else None,
                    'is_student': user.is_student,
                    'is_teacher': user.is_teacher,
                    'is_admin': user.is_admin
                }
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserInfoView(APIView):
    """获取用户信息"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def put(self, request):
        """更新用户信息和密码"""
        user = request.user
        
        try:
            # 获取请求数据
            data = request.data
            
            # 更新用户基本信息
            if 'name' in data:
                user.name = data['name']
            if 'phone' in data:
                user.phone = data['phone']
            if 'email' in data:
                user.email = data['email']
            if 'gender' in data:
                user.gender = data['gender']
            if 'birth_date' in data:
                import datetime
                try:
                    birth_date = datetime.datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
                    user.birth_date = birth_date
                except ValueError:
                    return Response({
                        'code': 400,
                        'message': '出生日期格式错误，应为YYYY-MM-DD'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # 处理密码修改
            if 'old_password' in data and 'new_password' in data:
                old_password = data['old_password']
                new_password = data['new_password']
                
                # 验证当前密码
                if not user.check_password(old_password):
                    return Response({
                        'code': 400,
                        'message': '当前密码错误'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # 设置新密码
                user.set_password(new_password)
            
            # 保存修改
            user.save()
            
            return Response({
                'code': 200,
                'message': '信息更新成功'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'信息更新失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AdminStatisticsView(APIView):
    """管理员统计信息"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # 仅允许管理员访问
        if request.user.user_type != 'admin':
            return Response({
                "code": 403,
                "message": "只有管理员可以访问此接口"
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # 导入所有申请模型
            from material.models import (
                EnglishScore,
                AcademicPaper,
                PatentWork,
                AcademicCompetition,
                InnovationProject,
                CCFCSPCertification,
                InternationalInternship,
                MilitaryService,
                VolunteerService,
                HonoraryTitle,
                SocialWork,
                SportsCompetition
            )
            
            # 统计学生、教师和管理员数量
            total_students = User.objects.filter(user_type='student').count()
            total_teachers = User.objects.filter(user_type='teacher').count()
            total_admins = User.objects.filter(user_type='admin').count()
            
            # 统计待审批和已审批申请数量
            pending_applications = 0
            approved_applications = 0
            
            # 统计所有申请状态
            for model in [
                EnglishScore,
                AcademicPaper,
                PatentWork,
                AcademicCompetition,
                InnovationProject,
                CCFCSPCertification,
                InternationalInternship,
                MilitaryService,
                VolunteerService,
                HonoraryTitle,
                SocialWork,
                SportsCompetition
            ]:
                # 待审批状态包括：pending（待一审）、first_reviewing（一审中）、second_reviewing（二审中）
                pending_count = model.objects.filter(
                    review_status__in=['pending', 'first_reviewing', 'second_reviewing']
                ).count()
                pending_applications += pending_count
                
                # 已审批状态包括：first_approved（一审通过）、approved（审核通过）、first_rejected（一审不通过）、rejected（审核不通过）
                approved_count = model.objects.filter(
                    review_status__in=['first_approved', 'approved', 'first_rejected', 'rejected']
                ).count()
                approved_applications += approved_count
            
            # 构建符合前端期望格式的统计数据
            statistics = {
                'user_type_stats': {
                    'students': total_students,
                    'teachers': total_teachers,
                    'admins': total_admins
                },
                'pending_applications': pending_applications,
                'approved_applications': approved_applications
            }
            
            return Response({
                'code': 200,
                'message': 'success',
                'data': statistics
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "code": 500,
                "message": f"获取统计信息失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CollegeManagementView(APIView):
    """学院管理"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # 允许管理员和教师访问
        if request.user.user_type not in ['admin', 'teacher']:
            return Response({
                "error": "只有管理员和教师可以访问此接口"
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            colleges = College.objects.all()
            college_list = [{
                'id': str(college.id),
                'name': college.name,
                'created_at': college.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': college.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            } for college in colleges]
            
            return Response({
                'code': 200,
                'message': 'success',
                'data': college_list
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "code": 500,
                "message": f"获取学院列表失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        # 仅允许管理员访问
        if request.user.user_type != 'admin':
            return Response({
                "error": "只有管理员可以访问此接口"
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            name = request.data.get('name')
            if not name:
                return Response({
                "code": 400,
                "message": "学院名称不能为空"
            }, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查学院是否已存在
            if College.objects.filter(name=name).exists():
                return Response({
                    "code": 400,
                    "message": "该学院已存在"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建学院
            college = College.objects.create(name=name)
            
            return Response({
                'code': 200,
                'message': '学院创建成功',
                'data': {
                    'id': str(college.id),
                    'name': college.name
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "code": 500,
                "message": f"创建学院失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, college_name):
        # 仅允许管理员访问
        if request.user.user_type != 'admin':
            return Response({
                "error": "只有管理员可以访问此接口"
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # 根据名称查找学院
            college = College.objects.get(name=college_name)
            college.delete()
            
            return Response({
                'code': 200,
                'message': '学院删除成功'
            }, status=status.HTTP_200_OK)
        except College.DoesNotExist:
            return Response({
                "code": 404,
                "message": "学院不存在"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "code": 500,
                "message": f"删除学院失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ClassManagementView(APIView):
    """班级管理"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, class_id=None):
        # 允许管理员和教师访问
        if request.user.user_type not in ['admin', 'teacher']:
            return Response({
                "error": "只有管理员和教师可以访问此接口"
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # 如果提供了class_id参数
            if class_id:
                # 获取班级对象
                cls = Class.objects.get(id=class_id)
                
                # 检查请求路径，判断是班级详情还是学生列表
                path = request.path
                if path.endswith('/students/'):
                    # 获取班级学生
                    students = User.objects.filter(clazz=cls, user_type='student')
                    # 使用UserSerializer序列化学生数据，确保获取正确的综测成绩
                    from .serializers import UserSerializer
                    serializer = UserSerializer(students, many=True)
                    student_list = serializer.data
                    # 处理序列化后的学生数据，确保格式一致
                    for student in student_list:
                        # 确保学号显示正确
                        student['student_id'] = student['school_id']
                        # 确保性别显示正确
                        student['gender'] = student['gender']
                        # 确保学院信息格式正确
                        if student['college']:
                            student['college'] = {
                                'id': student['college'],
                                'name': student['college_name']
                            }
                        # 确保班级信息格式正确
                        if student['class_id']:
                            student['class'] = {
                                'id': student['class_id'],
                                'name': student['class_name']
                            }
                        else:
                            student['class'] = None
                        # 移除不需要的字段，简化返回数据
                        student.pop('college_name', None)
                        student.pop('class_id', None)
                        student.pop('class_name', None)
                        student.pop('is_active', None)
                        student.pop('is_superuser', None)
                        student.pop('is_staff', None)
                        student.pop('is_student', None)
                        student.pop('is_teacher', None)
                        student.pop('is_admin', None)
                        student.pop('user_type', None)
                        student.pop('major', None)
                        student.pop('title', None)
                        student.pop('grade', None)  # 移除grade字段，避免重复
                        student.pop('contact', None)
                        student.pop('date_joined', None)
                        student.pop('major', None)
                        student.pop('title', None)
                    
                    return Response({
                        'code': 200,
                        'message': 'success',
                        'data': student_list
                    }, status=status.HTTP_200_OK)
                else:
                    # 返回班级详情
                    class_detail = {
                        'id': str(cls.id),
                        'name': cls.name,
                        'grade': cls.grade,
                        'college': {
                            'id': str(cls.college.id),
                            'name': cls.college.name
                        } if cls.college else None,
                        'created_at': cls.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'updated_at': cls.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    return Response({
                        'code': 200,
                        'message': 'success',
                        'data': class_detail
                    }, status=status.HTTP_200_OK)
            # 如果没有提供class_id参数，返回所有班级列表
            else:
                classes = Class.objects.all()
                class_list = [{
                    'id': str(cls.id),
                    'name': cls.name,
                    'grade': cls.grade,
                    'college': {
                        'id': str(cls.college.id),
                        'name': cls.college.name
                    } if cls.college else None,
                    'created_at': cls.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': cls.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                } for cls in classes]
                
                return Response({
                    'code': 200,
                    'message': 'success',
                    'data': class_list
                }, status=status.HTTP_200_OK)
        except Class.DoesNotExist:
            return Response({
                "code": 404,
                "message": "班级不存在"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "code": 500,
                "message": f"获取班级信息失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        # 仅允许管理员访问
        if request.user.user_type != 'admin':
            return Response({
                "error": "只有管理员可以访问此接口"
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # 调试：打印完整的请求体
            print(f"完整的请求体: {request.data}")
            print(f"请求体类型: {type(request.data)}")
            
            # 调试：打印请求头
            print(f"请求头: {request.headers}")
            
            # 获取绑定数据
            name = request.data.get('name')
            grade = request.data.get('grade')
            # 支持college和college_id两种字段名，兼容前端不同的传递方式
            college_id = request.data.get('college_id') or request.data.get('college')
            
            # 调试：打印请求数据
            print(f"请求数据: name={name}, grade={grade}, college_id={college_id}")
            # 调试：打印college_id的类型
            print(f"college_id的类型: {type(college_id)}")
            
            # 调试：遍历所有请求参数
            print("所有请求参数:")
            for key, value in request.data.items():
                print(f"  {key}: {value} (类型: {type(value)})")
            
            if not name:
                return Response({
                    "code": 400,
                    "message": "班级名称不能为空"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not college_id:
                return Response({
                    "code": 400,
                    "message": "所属学院不能为空"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取学院对象
            try:
                college = College.objects.get(id=college_id)
                print(f"学院对象获取成功: {college}")
            except College.DoesNotExist:
                print(f"学院不存在: college_id={college_id}")
                return Response({
                    "code": 404,
                    "message": "学院不存在"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 创建班级
            cls = Class.objects.create(
                name=name,
                grade=grade,
                college=college
            )
            print(f"班级创建成功: {cls}")
            
            return Response({
                'code': 200,
                'message': '班级创建成功',
                'data': {
                    'id': str(cls.id),
                    'name': cls.name,
                    'grade': cls.grade,
                    'college': {
                        'id': str(college.id),
                        'name': college.name
                    }
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            # 调试：打印错误信息
            print(f"创建班级失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({
                "code": 500,
                "message": f"创建班级失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, class_id):
        # 仅允许管理员访问
        if request.user.user_type != 'admin':
            return Response({
                "error": "只有管理员可以访问此接口"
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # 根据ID查找班级
            cls = Class.objects.get(id=class_id)
            cls.delete()
            
            return Response({
                'code': 200,
                'message': '班级删除成功'
            }, status=status.HTTP_200_OK)
        except Class.DoesNotExist:
            return Response({
                "code": 404,
                "message": "班级不存在"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "code": 500,
                "message": f"删除班级失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AccountManagementView(APIView):
    """账号管理"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            'success': True,
            'data': []
        }, status=status.HTTP_200_OK)

class StudentManagementView(APIView):
    """学生管理"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # 允许管理员和教师访问
        if request.user.user_type not in ['admin', 'teacher']:
            return Response({
                "error": "只有管理员和教师可以访问此接口"
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # 获取查询参数
            search = request.GET.get('search', '')
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 10))
            
            # 构建查询
            query = User.objects.filter(user_type='student')
            
            # 权限控制：
            # 管理员可以看到所有学生信息
            # 教师只能看到自己管辖班级的学生信息
            if request.user.user_type == 'teacher':
                # 获取教师管辖的所有班级
                teacher_classes = request.user.class_bindings.values_list('class_obj_id', flat=True)
                # 过滤出学生所在班级在教师管辖班级列表中的学生
                query = query.filter(clazz_id__in=teacher_classes)
            
            # 搜索过滤
            if search:
                query = query.filter(
                    models.Q(school_id__icontains=search) |
                    models.Q(name__icontains=search) |
                    models.Q(college__name__icontains=search)
                )
            
            # 分页
            total = query.count()
            students = query[(page-1)*page_size:page*page_size]
            
            # 构建响应数据
            student_list = [{
                'id': str(student.id),
                'school_id': student.school_id,
                'name': student.name,
                'gender': student.gender,
                'grade': student.grade,
                'major': student.major,
                'gpa': student.gpa,
                'college': {
                    'id': str(student.college.id),
                    'name': student.college.name
                } if student.college else None,
                'class': {
                    'id': str(student.clazz.id),
                    'name': student.clazz.name
                } if student.clazz else None,
                'contact': student.contact,
                'counselors': student.counselors,
                'counselor_names': student.counselor_names,
                'created_at': student.date_joined.strftime('%Y-%m-%d %H:%M:%S')
            } for student in students]
            
            return Response({
                'code': 200,
                'message': 'success',
                'data': {
                    'results': student_list,
                    'count': total,
                    'page': page,
                    'page_size': page_size
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": f"获取学生列表失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TeacherManagementView(APIView):
    """教师管理"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # 允许管理员和教师访问
        if request.user.user_type not in ['admin', 'teacher']:
            return Response({
                "error": "只有管理员和教师可以访问此接口"
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # 获取查询参数
            search = request.GET.get('search', '')
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 10))
            
            # 构建查询
            query = User.objects.filter(user_type='teacher')
            
            # 搜索过滤
            if search:
                query = query.filter(
                    models.Q(school_id__icontains=search) |
                    models.Q(name__icontains=search) |
                    models.Q(college__name__icontains=search)
                )
            
            # 分页
            total = query.count()
            teachers = query[(page-1)*page_size:page*page_size]
            
            # 构建响应数据
            teacher_list = [{
                'id': str(teacher.id),
                'school_id': teacher.school_id,
                'name': teacher.name,
                'gender': teacher.gender,
                'title': teacher.title,
                'college': {
                    'id': str(teacher.college.id),
                    'name': teacher.college.name
                } if teacher.college else None,
                'contact': teacher.contact,
                'created_at': teacher.date_joined.strftime('%Y-%m-%d %H:%M:%S')
            } for teacher in teachers]
            
            return Response({
                'code': 200,
                'message': 'success',
                'data': {
                    'results': teacher_list,
                    'count': total,
                    'page': page,
                    'page_size': page_size
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": f"获取教师列表失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AdminUserListView(APIView):
    """管理员用户列表"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # 仅允许管理员访问
        if request.user.user_type != 'admin':
            return Response({
                "error": "只有管理员可以访问此接口"
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # 获取查询参数
            user_type = request.GET.get('type')
            search = request.GET.get('search', '')
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 10))
            
            # 构建查询
            query = User.objects.all()
            
            # 按用户类型过滤
            if user_type:
                query = query.filter(user_type=user_type)
            
            # 搜索过滤
            if search:
                query = query.filter(
                    models.Q(school_id__icontains=search) |
                    models.Q(name__icontains=search) |
                    models.Q(college__name__icontains=search)
                )
            
            # 分页
            total = query.count()
            users = query[(page-1)*page_size:page*page_size]
            
            # 使用UserSerializer序列化数据
            serializer = UserSerializer(users, many=True)
            user_list = serializer.data
            
            # 处理分页响应
            return Response({
                'code': 200,
                'message': 'success',
                'data': {
                    'results': user_list,
                    'count': total,
                    'page': page,
                    'page_size': page_size
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": f"获取用户列表失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserManagementView(APIView):
    """用户管理"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id=None):
        # 仅允许管理员访问
        if request.user.user_type != 'admin':
            return Response({
                "code": 403,
                "message": "只有管理员可以访问此接口"
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # 检查请求体中是否有user_id（用于更新用户）
            request_user_id = request.data.get('user_id')
            
            # 情况1：URL中提供了user_id，说明是重置密码
            if user_id:
                # 重置密码逻辑
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    return Response({
                        "code": 404,
                        "message": "用户不存在"
                    }, status=status.HTTP_404_NOT_FOUND)
                
                # 获取新密码，如果没有提供则使用工号后六位作为默认密码
                new_password = request.data.get('password', user.school_id[-6:])
                
                # 设置新密码
                user.set_password(new_password)
                user.save()
                
                return Response({
                    'code': 200,
                    'message': '密码重置成功',
                    'data': {
                        'default_password': new_password  # 返回实际使用的默认密码，让前端显示给用户
                    }
                }, status=status.HTTP_200_OK)
            # 情况2：请求体中提供了user_id，说明是更新用户信息
            elif request_user_id:
                # 更新用户信息逻辑
                try:
                    user = User.objects.get(id=request_user_id)
                except User.DoesNotExist:
                    return Response({
                        "code": 404,
                        "message": "用户不存在"
                    }, status=status.HTTP_404_NOT_FOUND)
                
                # 更新用户信息
                school_id = request.data.get('school_id')
                name = request.data.get('name')
                gender = request.data.get('gender')
                contact = request.data.get('contact')
                # 支持college和college_id两种字段名，兼容前端不同的传递方式
                college_id = request.data.get('college_id') or request.data.get('college')
                # 支持class_id和class_name两种字段名，兼容前端不同的传递方式
                class_id = request.data.get('class_id') or request.data.get('class_name')
                grade = request.data.get('grade')
                major = request.data.get('major')
                title = request.data.get('title')
                gpa = request.data.get('gpa')
                
                # 更新用户信息
                if school_id:
                    # 检查新的工号/学号是否与其他用户冲突
                    existing_user = User.objects.filter(school_id=school_id).exclude(id=request_user_id).first()
                    if existing_user:
                        return Response({
                            "code": 400,
                            "message": "该用户已存在"
                        }, status=status.HTTP_400_BAD_REQUEST)
                    user.school_id = school_id
                if name:
                    user.name = name
                if gender:
                    user.gender = gender
                if contact:
                    user.contact = contact
                if grade:
                    user.grade = grade
                if major:
                    user.major = major
                if title:
                    user.title = title
                if gpa is not None:
                    user.gpa = gpa
                
                # 更新学院
                if college_id:
                    try:
                        college = College.objects.get(id=college_id)
                        user.college = college
                    except College.DoesNotExist:
                        return Response({
                            "code": 404,
                            "message": "学院不存在"
                        }, status=status.HTTP_404_NOT_FOUND)
                
                # 更新班级
                if class_id:
                    try:
                        clazz = Class.objects.get(id=class_id)
                        user.clazz = clazz
                    except Class.DoesNotExist:
                        return Response({
                            "code": 404,
                            "message": "班级不存在"
                        }, status=status.HTTP_404_NOT_FOUND)
                
                # 保存更新
                user.save()
                
                return Response({
                    'code': 200,
                    'message': '用户更新成功',
                    'data': {
                        'id': str(user.id),
                        'school_id': user.school_id,
                        'name': user.name
                    }
                }, status=status.HTTP_200_OK)
            # 情况3：既没有URL中的user_id，也没有请求体中的user_id，说明是创建用户
            else:
                # 创建用户逻辑
                # 获取用户数据
                school_id = request.data.get('school_id')
                name = request.data.get('name')
                user_type = request.data.get('user_type', 'student')
                college_id = request.data.get('college_id')
                password = request.data.get('password', '123456')  # 默认密码
                
                # 验证必填字段
                if not school_id or not name:
                    return Response({
                        "code": 400,
                        "message": "学号/工号和姓名不能为空"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # 获取学院对象
                college = None
                # 支持从college字段获取学院ID，兼容前端可能传递的不同字段名
                college_id = request.data.get('college_id') or request.data.get('college')
                if college_id:
                    try:
                        college = College.objects.get(id=college_id)
                    except College.DoesNotExist:
                        return Response({
                            "code": 404,
                            "message": "学院不存在"
                        }, status=status.HTTP_404_NOT_FOUND)
                
                # 检查用户是否已存在
                if User.objects.filter(school_id=school_id).exists():
                    return Response({
                        "code": 400,
                        "message": "该用户已存在"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # 创建用户
                user = User.objects.create_user(
                    school_id=school_id,
                    name=name,
                    user_type=user_type,
                    college=college,
                    password=password
                )
                
                return Response({
                    'code': 200,
                    'message': '用户创建成功',
                    'data': {
                        'id': str(user.id),
                        'school_id': user.school_id,
                        'name': user.name,
                        'user_type': user.user_type
                    }
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "code": 500,
                "message": f"操作失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, user_id):
        # 仅允许管理员访问
        if request.user.user_type != 'admin':
            return Response({
                "error": "只有管理员可以访问此接口"
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # 删除用户
            user = User.objects.get(id=user_id)
            user.delete()
            
            return Response({
                'code': 200,
                'message': '用户删除成功'
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                "error": "用户不存在"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "error": f"删除用户失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        # 仅允许管理员访问
        if request.user.user_type != 'admin':
            return Response({
                "error": "只有管理员可以访问此接口"
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # 获取用户数据
            user_id = request.data.get('user_id')
            if not user_id:
                return Response({
                    "error": "用户ID不能为空"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取用户对象
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({
                    "error": "用户不存在"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 更新用户信息
            name = request.data.get('name')
            gender = request.data.get('gender')
            contact = request.data.get('contact')
            college_id = request.data.get('college_id')
            grade = request.data.get('grade')
            major = request.data.get('major')
            title = request.data.get('title')
            gpa = request.data.get('gpa')
            
            if name:
                user.name = name
            if gender:
                user.gender = gender
            if contact:
                user.contact = contact
            if grade:
                user.grade = grade
            if major:
                user.major = major
            if title:
                user.title = title
            if gpa is not None:
                user.gpa = gpa
            
            # 更新学院
            if college_id:
                try:
                    college = College.objects.get(id=college_id)
                    user.college = college
                except College.DoesNotExist:
                    return Response({
                        "error": "学院不存在"
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # 保存更新
            user.save()
            
            return Response({
                'code': 200,
                'message': '用户更新成功',
                'data': {
                    'id': str(user.id),
                    'school_id': user.school_id,
                    'name': user.name
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": f"更新用户失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ClassBindingView(APIView):
    """班级绑定管理"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # 仅允许管理员访问
        if request.user.user_type != 'admin':
            return Response({
                "error": "只有管理员可以访问此接口"
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # 获取查询参数
            teacher_id = request.GET.get('teacher_id')
            
            # 构建查询
            query = ClassBinding.objects.all()
            
            # 按教师ID过滤
            if teacher_id:
                query = query.filter(teacher_id=teacher_id)
            
            # 构建响应数据
            binding_list = [{
                'id': str(binding.id),
                'teacher': {
                    'id': str(binding.teacher.id),
                    'school_id': binding.teacher.school_id,
                    'name': binding.teacher.name,
                    'title': binding.teacher.title,
                    'college': binding.teacher.college.name if binding.teacher.college else None
                },
                'class': {
                    'id': str(binding.class_obj.id),
                    'name': binding.class_obj.name,
                    'grade': binding.class_obj.grade,
                    'college': binding.class_obj.college.name if binding.class_obj.college else None
                },
                'created_at': binding.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for binding in query]
            
            return Response({
                'code': 200,
                'message': 'success',
                'data': binding_list
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": f"获取班级绑定列表失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        # 仅允许管理员访问
        if request.user.user_type != 'admin':
            return Response({
                "error": "只有管理员可以访问此接口"
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # 获取绑定数据
            teacher_id = request.data.get('teacher_id')
            class_id = request.data.get('class_id')
            
            if not teacher_id or not class_id:
                return Response({
                    "error": "教师ID和班级ID不能为空"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取教师和班级对象
            try:
                teacher = User.objects.get(id=teacher_id, user_type='teacher')
            except User.DoesNotExist:
                return Response({
                    "error": "教师不存在"
                }, status=status.HTTP_404_NOT_FOUND)
            
            try:
                class_obj = Class.objects.get(id=class_id)
            except Class.DoesNotExist:
                return Response({
                    "error": "班级不存在"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 检查绑定是否已存在
            if ClassBinding.objects.filter(teacher=teacher, class_obj=class_obj).exists():
                return Response({
                    "error": "该绑定已存在"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建绑定
            binding = ClassBinding.objects.create(
                teacher=teacher,
                class_obj=class_obj
            )
            
            return Response({
                'code': 200,
                'message': '绑定成功',
                'data': {
                    'id': str(binding.id),
                    'teacher_id': str(teacher.id),
                    'class_id': str(class_obj.id)
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "error": f"创建绑定失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, binding_id):
        # 仅允许管理员访问
        if request.user.user_type != 'admin':
            return Response({
                "error": "只有管理员可以访问此接口"
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # 删除绑定
            binding = ClassBinding.objects.get(id=binding_id)
            binding.delete()
            
            return Response({
                'code': 200,
                'message': '解除绑定成功'
            }, status=status.HTTP_200_OK)
        except ClassBinding.DoesNotExist:
            return Response({
                "error": "绑定不存在"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "error": f"解除绑定失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


