from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from abc import ABC, abstractmethod
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Q
import os
from uuid import uuid4

from .models import (
    EnglishScore, AcademicPaper, PatentWork, AcademicCompetition,
    InnovationProject, CCFCSPCertification, InternationalInternship,
    MilitaryService, VolunteerService, HonoraryTitle, SocialWork, SportsCompetition
)
from .serializers import (
    EnglishScoreSerializer, EnglishScoreCreateSerializer,
    AcademicPaperSerializer, AcademicPaperCreateSerializer,
    PatentWorkSerializer, PatentWorkCreateSerializer,
    AcademicCompetitionSerializer, AcademicCompetitionCreateSerializer,
    InnovationProjectSerializer, InnovationProjectCreateSerializer,
    CCFCSPCertificationSerializer, CCFCSPCertificationCreateSerializer,
    InternationalInternshipSerializer, InternationalInternshipCreateSerializer,
    MilitaryServiceSerializer, MilitaryServiceCreateSerializer,
    VolunteerServiceSerializer, VolunteerServiceCreateSerializer,
    HonoraryTitleSerializer, HonoraryTitleCreateSerializer,
    SocialWorkSerializer, SocialWorkCreateSerializer,
    SportsCompetitionSerializer, SportsCompetitionCreateSerializer,
    ApplicationSummarySerializer
)


def collect_attachments(application, model):
    attachments = []
    
    # 获取所有可能的附件字段
    attachment_fields = [
        'attachments', 'score_report', 'screenshot', 'file_url', 'path',
        'proof_materials', 'materials', 'documents', 'paper_attachments',
        'academic_paper_attachments', 'document_urls', 'file_urls', 'file_paths',
        'attachment_urls', 'file', 'proof_file', 'evidence_file',
        'supporting_document', 'report', 'certificate', 'diploma',
        'award_certificate', 'competition_certificate', 'volunteer_certificate'
    ]
    
    # 首先遍历模型的所有字段，查找FileField和ImageField类型的字段
    for field in model._meta.get_fields():
        field_name = field.name
        
        # 处理FileField和ImageField类型的字段
        if hasattr(field, '__class__') and field.__class__.__name__ in ['FileField', 'ImageField']:
            file = getattr(application, field_name, None)
            if file and hasattr(file, 'name') and file.name:
                try:
                    file_url = file.url if hasattr(file, 'url') else str(file)
                    attachments.append({
                        'name': field_name,
                        'url': file_url,
                        'original_name': file.name
                    })
                except Exception as e:
                    print(f"Error processing attachment {field_name}: {str(e)}")
    
    # 然后处理所有可能的附件字段，无论类型
    for field_name in attachment_fields:
        if hasattr(application, field_name):
            value = getattr(application, field_name)
            if value:
                # 处理单个文件对象
                if hasattr(value, 'name') and value.name:
                    try:
                        file_url = value.url if hasattr(value, 'url') else str(value)
                        attachments.append({
                            'name': field_name,
                            'url': file_url,
                            'original_name': value.name
                        })
                    except Exception as e:
                        print(f"Error processing attachment {field_name}: {str(e)}")
                # 处理字符串URL
                elif isinstance(value, str) and (value.startswith('http://') or value.startswith('https://') or value.startswith('/')):
                    attachments.append({
                        'name': field_name,
                        'url': value,
                        'original_name': value.split('/')[-1] if '/' in value else value
                    })
                # 处理文件URL列表
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, str) and (item.startswith('http://') or item.startswith('https://') or item.startswith('/')):
                            attachments.append({
                                'name': f"{field_name}_{i+1}",
                                'url': item,
                                'original_name': item.split('/')[-1] if '/' in item else item
                            })
                        # 处理列表中的文件对象
                        elif hasattr(item, 'name') and item.name:
                            try:
                                file_url = item.url if hasattr(item, 'url') else str(item)
                                attachments.append({
                                    'name': f"{field_name}_{i+1}",
                                    'url': file_url,
                                    'original_name': item.name
                                })
                            except Exception as e:
                                print(f"Error processing attachment {field_name}_{i+1}: {str(e)}")
    
    return attachments


class BaseApplicationViewSet(viewsets.ViewSet, ABC):
    permission_classes = [IsAuthenticated]
    
    @abstractmethod
    def get_serializer_class(self):
        pass
    
    @abstractmethod
    def get_model(self):
        pass
    
    @abstractmethod
    def get_view_name(self):
        pass
    
    def list(self, request):
        user = request.user
        if not hasattr(user, 'user_type') or user.user_type != 'student':
            return Response({
                "error": f"只有学生可以查看{self.get_view_name()}申请"
            }, status=status.HTTP_403_FORBIDDEN)
        
        model = self.get_model()
        queryset = model.objects.filter(user=user)
        serializer = self.get_serializer_class()(queryset, many=True, context={'request': request})
        return Response({
            "success": True,
            "data": serializer.data
        })
    
    def retrieve(self, request, pk=None):
        user = request.user
        if not hasattr(user, 'user_type') or user.user_type != 'student':
            return Response({
                "error": f"只有学生可以查看{self.get_view_name()}申请详情"
            }, status=status.HTTP_403_FORBIDDEN)
        
        model = self.get_model()
        try:
            application = model.objects.get(id=pk, user=user)
        except model.DoesNotExist:
            return Response({
                "error": f"{self.get_view_name()}申请不存在"
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer_class()(application, context={'request': request})
        return Response({
            "success": True,
            "data": serializer.data
        })
    
    def create(self, request):
        user = request.user
        if not hasattr(user, 'user_type') or user.user_type != 'student':
            return Response({
                "error": f"只有学生可以创建{self.get_view_name()}申请"
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer_class()(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({
                "success": True,
                "data": serializer.data,
                "message": f"{self.get_view_name()}申请创建成功"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "error": f"{self.get_view_name()}申请创建失败",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        user = request.user
        if not hasattr(user, 'user_type') or user.user_type != 'student':
            return Response({
                "error": f"只有学生可以更新{self.get_view_name()}申请"
            }, status=status.HTTP_403_FORBIDDEN)
        
        model = self.get_model()
        try:
            application = model.objects.get(id=pk, user=user)
        except model.DoesNotExist:
            return Response({
                "error": f"{self.get_view_name()}申请不存在"
            }, status=status.HTTP_404_NOT_FOUND)
        
        if application.review_status != 'pending':
            return Response({
                "error": "只有待审核状态的申请可以更新"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer_class()(application, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "data": serializer.data,
                "message": f"{self.get_view_name()}申请更新成功"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": f"{self.get_view_name()}申请更新失败",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        user = request.user
        if not hasattr(user, 'user_type') or user.user_type != 'student':
            return Response({
                "error": f"只有学生可以删除{self.get_view_name()}申请"
            }, status=status.HTTP_403_FORBIDDEN)
        
        model = self.get_model()
        try:
            application = model.objects.get(id=pk, user=user)
        except model.DoesNotExist:
            return Response({
                "error": f"{self.get_view_name()}申请不存在"
            }, status=status.HTTP_404_NOT_FOUND)
        
        if application.review_status not in ['pending', 'withdrawn', 'rejected', 'first_rejected', 'second_rejected', 'third_rejected']:
            return Response({
                "error": "当前状态的申请不可删除"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        application.delete()
        return Response({
            "success": True,
            "message": f"{self.get_view_name()}申请删除成功"
        }, status=status.HTTP_204_NO_CONTENT)


class StudentApplicationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        if not hasattr(user, 'user_type') or user.user_type != 'student':
            return Response({
                "error": "只有学生可以查看申请列表"
            }, status=status.HTTP_403_FORBIDDEN)

        applications = []

        application_models = [
            (EnglishScore, 'english_scores'),
            (AcademicPaper, 'academic_papers'),
            (PatentWork, 'patent_works'),
            (AcademicCompetition, 'academic_competitions'),
            (InnovationProject, 'innovation_projects'),
            (CCFCSPCertification, 'ccf_csp_certifications'),
            (InternationalInternship, 'international_internships'),
            (MilitaryService, 'military_services'),
            (VolunteerService, 'volunteer_services'),
            (HonoraryTitle, 'honorary_titles'),
            (SocialWork, 'social_works'),
            (SportsCompetition, 'sports_competitions'),
        ]

        for model, model_name in application_models:
            queryset = model.objects.filter(user=user).order_by('-created_at')
            for application in queryset:
                project_name = ""
                if model_name == 'english_scores':
                    project_name = f"{application.get_exam_type_display()}"
                elif model_name == 'academic_papers':
                    project_name = application.paper_title or "学术论文加分申请"
                elif model_name == 'patent_works':
                    project_name = application.paper_title or "专利著作加分申请"
                elif model_name == 'academic_competitions':
                    project_name = application.competition_specific_name or application.competition_name or "学业竞赛加分申请"
                elif model_name == 'innovation_projects':
                    project_name = application.project_name or "创新项目加分申请"
                elif model_name == 'ccf_csp_certifications':
                    project_name = f"CCF CSP认证_{application.score}"
                elif model_name == 'international_internships':
                    project_name = application.organization_name or "国际实习加分申请"
                elif model_name == 'military_services':
                    project_name = f"参军入伍服兵役加分申请_一年以上两年以内"
                elif model_name == 'volunteer_services':
                    project_name = application.activity_name or "志愿服务加分申请"
                elif model_name == 'honorary_titles':
                    project_name = application.title_name or "荣誉称号加分申请"
                elif model_name == 'social_works':
                    project_name = application.organization or "社会工作加分申请"
                elif model_name == 'sports_competitions':
                    project_name = application.competition_name or "体育竞赛加分申请"

                attachments = collect_attachments(application, model)

                # Map category to correct type names for front-end display
                category_map = {
                    'english_scores': 'english',
                    'academic_papers': 'academic_paper',
                    'patent_works': 'patent_work',
                    'academic_competitions': 'academic_competition',
                    'innovation_projects': 'innovation',
                    'ccf_csp_certifications': 'ccf_csp',
                    'international_internships': 'internship',
                    'military_services': 'military',
                    'volunteer_services': 'volunteer_service',
                    'honorary_titles': 'honor',
                    'social_works': 'social',
                    'sports_competitions': 'sports_competition'
                }
                category = category_map[model_name]

                # 获取预估分数，确保正确处理None值和字符串类型
                estimated_score = getattr(application, 'estimated_score', 0)
                try:
                    score = float(estimated_score) if estimated_score is not None else 0.0
                except (ValueError, TypeError):
                    score = 0.0
                    
                applications.append({
                    "id": str(application.id),
                    "category": category,
                    "title": project_name,
                    "score": score,
                    "applyDate": application.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "review_status": application.review_status,
                    "attachments": attachments
                })

        return Response({
            "success": True,
            "data": applications
        })

    def retrieve(self, request, pk=None):
        user = request.user
        if not hasattr(user, 'user_type') or user.user_type != 'student':
            return Response({
                "error": "只有学生可以查看申请详情"
            }, status=status.HTTP_403_FORBIDDEN)

        application_id = pk
        application_type = request.query_params.get('type')
        application = None
        model = None

        # 支持的申请模型列表
        application_models = [
            EnglishScore, AcademicPaper, PatentWork, AcademicCompetition,
            InnovationProject, CCFCSPCertification, InternationalInternship,
            MilitaryService, VolunteerService, HonoraryTitle, SocialWork,
            SportsCompetition
        ]

        # 如果没有提供type参数，自动尝试通过id查找申请
        if not application_type:
            for model_candidate in application_models:
                try:
                    application = model_candidate.objects.get(id=application_id, user=user)
                    model = model_candidate
                    break
                except model_candidate.DoesNotExist:
                    continue
        else:
            # 根据type参数获取对应的模型
            model_mapping = {
                'english_scores': EnglishScore,
                'academic_papers': AcademicPaper,
                'patent_works': PatentWork,
                'academic_competitions': AcademicCompetition,
                'innovation_projects': InnovationProject,
                'ccf_csp_certifications': CCFCSPCertification,
                'international_internships': InternationalInternship,
                'military_services': MilitaryService,
                'volunteer_services': VolunteerService,
                'honorary_titles': HonoraryTitle,
                'social_works': SocialWork,
                'sports_competitions': SportsCompetition,
            }

            if application_type not in model_mapping:
                return Response({
                    "error": "无效的申请类型"
                }, status=status.HTTP_400_BAD_REQUEST)

            model = model_mapping[application_type]
            try:
                application = model.objects.get(id=application_id, user=user)
            except model.DoesNotExist:
                return Response({
                    "error": "申请不存在"
                }, status=status.HTTP_404_NOT_FOUND)

        # 检查申请是否存在
        if not application:
            return Response({
                "error": "申请不存在"
            }, status=status.HTTP_404_NOT_FOUND)

        # 获取对应的序列化器
        serializer_map = {
            EnglishScore: EnglishScoreSerializer,
            AcademicPaper: AcademicPaperSerializer,
            PatentWork: PatentWorkSerializer,
            AcademicCompetition: AcademicCompetitionSerializer,
            InnovationProject: InnovationProjectSerializer,
            CCFCSPCertification: CCFCSPCertificationSerializer,
            InternationalInternship: InternationalInternshipSerializer,
            MilitaryService: MilitaryServiceSerializer,
            VolunteerService: VolunteerServiceSerializer,
            HonoraryTitle: HonoraryTitleSerializer,
            SocialWork: SocialWorkSerializer,
            SportsCompetition: SportsCompetitionSerializer,
        }

        serializer_class = serializer_map.get(model)
        if not serializer_class:
            return Response({
                "error": "找不到对应的序列化器"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = serializer_class(application, context={'request': request})

        attachments = collect_attachments(application, model)

        # 获取application_type用于返回
        if not application_type:
            # 反向查找application_type
            reverse_model_mapping = {
                EnglishScore: 'english_scores',
                AcademicPaper: 'academic_papers',
                PatentWork: 'patent_works',
                AcademicCompetition: 'academic_competitions',
                InnovationProject: 'innovation_projects',
                CCFCSPCertification: 'ccf_csp_certifications',
                InternationalInternship: 'international_internships',
                MilitaryService: 'military_services',
                VolunteerService: 'volunteer_services',
                HonoraryTitle: 'honorary_titles',
                SocialWork: 'social_works',
                SportsCompetition: 'sports_competitions',
            }
            application_type = reverse_model_mapping.get(model, '')

        return Response({
            "success": True,
            "data": {
                "application_type": application_type,
                "application_data": serializer.data,
                "attachments": attachments
            }
        })

    def destroy(self, request, pk=None):
        user = request.user
        if not hasattr(user, 'user_type') or user.user_type != 'student':
            return Response({
                "error": "只有学生可以删除申请"
            }, status=status.HTTP_403_FORBIDDEN)

        application_id = pk
        application_type = request.query_params.get('type')
        application = None

        # 支持的申请模型列表
        application_models = [
            EnglishScore, AcademicPaper, PatentWork, AcademicCompetition,
            InnovationProject, CCFCSPCertification, InternationalInternship,
            MilitaryService, VolunteerService, HonoraryTitle, SocialWork,
            SportsCompetition
        ]

        # 如果没有提供type参数，自动尝试通过id查找申请
        if not application_type:
            for model in application_models:
                try:
                    application = model.objects.get(id=application_id, user=user)
                    break
                except model.DoesNotExist:
                    continue
        else:
            # 根据type参数获取对应的模型
            model_mapping = {
                'english_scores': EnglishScore,
                'academic_papers': AcademicPaper,
                'patent_works': PatentWork,
                'academic_competitions': AcademicCompetition,
                'innovation_projects': InnovationProject,
                'ccf_csp_certifications': CCFCSPCertification,
                'international_internships': InternationalInternship,
                'military_services': MilitaryService,
                'volunteer_services': VolunteerService,
                'honorary_titles': HonoraryTitle,
                'social_works': SocialWork,
                'sports_competitions': SportsCompetition,
            }

            if application_type not in model_mapping:
                return Response({
                    "error": "无效的申请类型"
                }, status=status.HTTP_400_BAD_REQUEST)

            model = model_mapping[application_type]
            try:
                application = model.objects.get(id=application_id, user=user)
            except model.DoesNotExist:
                return Response({
                    "error": "申请不存在"
                }, status=status.HTTP_404_NOT_FOUND)

        # 检查申请是否存在
        if not application:
            return Response({
                "error": "申请不存在"
            }, status=status.HTTP_404_NOT_FOUND)

        if application.review_status not in ['pending', 'withdrawn', 'rejected', 'first_rejected', 'second_rejected', 'third_rejected']:
            return Response({
                "error": "当前状态的申请不可删除"
            }, status=status.HTTP_400_BAD_REQUEST)

        application.delete()
        return Response({
            "success": True,
            "message": "申请删除成功"
        }, status=status.HTTP_204_NO_CONTENT)

    def update(self, request, pk=None):
        user = request.user
        if not hasattr(user, 'user_type') or user.user_type != 'student':
            return Response({
                "error": "只有学生可以更新申请"
            }, status=status.HTTP_403_FORBIDDEN)
        
        application_id = pk
        application_type = request.query_params.get('type') or request.data.get('application_type')

        if not application_type:
            return Response({
                "error": "缺少申请类型参数"
            }, status=status.HTTP_400_BAD_REQUEST)

        model_mapping = {
            'english_scores': EnglishScore,
            'academic_papers': AcademicPaper,
            'patent_works': PatentWork,
            'academic_competitions': AcademicCompetition,
            'innovation_projects': InnovationProject,
            'ccf_csp_certifications': CCFCSPCertification,
            'international_internships': InternationalInternship,
            'military_services': MilitaryService,
            'volunteer_services': VolunteerService,
            'honorary_titles': HonoraryTitle,
            'social_works': SocialWork,
            'sports_competitions': SportsCompetition,
        }

        if application_type not in model_mapping:
            return Response({
                "error": "无效的申请类型"
            }, status=status.HTTP_400_BAD_REQUEST)

        model = model_mapping[application_type]
        try:
            application = model.objects.get(id=application_id, user=user)
        except model.DoesNotExist:
            return Response({
                "error": "申请不存在"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = {
            'english_scores': EnglishScoreSerializer,
            'academic_papers': AcademicPaperSerializer,
            'patent_works': PatentWorkSerializer,
            'academic_competitions': AcademicCompetitionSerializer,
            'innovation_projects': InnovationProjectSerializer,
            'ccf_csp_certifications': CCFCSPCertificationSerializer,
            'international_internships': InternationalInternshipSerializer,
            'military_services': MilitaryServiceSerializer,
            'volunteer_services': VolunteerServiceSerializer,
            'honorary_titles': HonoraryTitleSerializer,
            'social_works': SocialWorkSerializer,
            'sports_competitions': SportsCompetitionSerializer,
        }[application_type](application, data=request.data, context={'request': request}, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "data": serializer.data,
                "message": "申请更新成功"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "申请更新失败",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def application_summary(self, request):
        user = request.user
        if not hasattr(user, 'user_type') or user.user_type != 'student':
            return Response(
                {"error": "只有学生可以查看申请汇总"},
                status=status.HTTP_403_FORBIDDEN
            )

        summary_data = {
            'english_scores': EnglishScore.objects.filter(user=user),
            'academic_papers': AcademicPaper.objects.filter(user=user),
            'patent_works': PatentWork.objects.filter(user=user),
            'academic_competitions': AcademicCompetition.objects.filter(user=user),
            'innovation_projects': InnovationProject.objects.filter(user=user),
            'ccf_csp_certifications': CCFCSPCertification.objects.filter(user=user),
            'international_internships': InternationalInternship.objects.filter(user=user),
            'military_services': MilitaryService.objects.filter(user=user),
            'volunteer_services': VolunteerService.objects.filter(user=user),
            'honorary_titles': HonoraryTitle.objects.filter(user=user),
            'social_works': SocialWork.objects.filter(user=user),
            'sports_competitions': SportsCompetition.objects.filter(user=user),
        }

        serializer = ApplicationSummarySerializer(summary_data)
        return Response({
            "success": True,
            "data": serializer.data
        })

    @action(detail=False, methods=['get'])
    def application_stats(self, request):
        """获取申请统计信息"""
        user = request.user

        if not hasattr(user, 'user_type') or user.user_type != 'student':
            return Response(
                {"error": "只有学生可以查看申请统计"},
                status=status.HTTP_403_FORBIDDEN
            )

        # 统计各类申请的数量和状态
        models = {
            'english_scores': EnglishScore,
            'academic_papers': AcademicPaper,
            'patent_works': PatentWork,
            'academic_competitions': AcademicCompetition,
            'innovation_projects': InnovationProject,
            'ccf_csp_certifications': CCFCSPCertification,
            'international_internships': InternationalInternship,
            'military_services': MilitaryService,
            'volunteer_services': VolunteerService,
            'honorary_titles': HonoraryTitle,
            'social_works': SocialWork,
            'sports_competitions': SportsCompetition,
        }

        stats = {}
        total_applications = 0
        pending_applications = 0
        approved_applications = 0
        rejected_applications = 0

        for model_name, model in models.items():
            queryset = model.objects.filter(user=user)
            stats[model_name] = {
                'total': queryset.count(),
                'pending': queryset.filter(review_status='pending').count(),
                'approved': queryset.filter(review_status='approved').count(),
                'rejected': queryset.filter(review_status='rejected').count(),
                'withdrawn': queryset.filter(review_status='withdrawn').count()
            }
            
            # 更新总统计
            total_applications += stats[model_name]['total']
            pending_applications += stats[model_name]['pending']
            approved_applications += stats[model_name]['approved']
            rejected_applications += stats[model_name]['rejected']

        return Response({
            "success": True,
            "data": {
                "total_applications": total_applications,
                "pending_applications": pending_applications,
                "approved_applications": approved_applications,
                "rejected_applications": rejected_applications,
                "application_stats": stats
            }
        }, status=status.HTTP_200_OK)


class EnglishScoreViewSet(BaseApplicationViewSet):
    def get_serializer_class(self):
        return EnglishScoreSerializer
    
    def get_model(self):
        return EnglishScore
    
    def get_view_name(self):
        return "英语成绩"


class AcademicPaperViewSet(BaseApplicationViewSet):
    def get_serializer_class(self):
        return AcademicPaperSerializer
    
    def get_model(self):
        return AcademicPaper
    
    def get_view_name(self):
        return "学术论文"


class PatentWorkViewSet(BaseApplicationViewSet):
    def get_serializer_class(self):
        return PatentWorkSerializer
    
    def get_model(self):
        return PatentWork
    
    def get_view_name(self):
        return "专利作品"


class AcademicCompetitionViewSet(BaseApplicationViewSet):
    def get_serializer_class(self):
        return AcademicCompetitionSerializer
    
    def get_model(self):
        return AcademicCompetition
    
    def get_view_name(self):
        return "学术竞赛"


class InnovationProjectViewSet(BaseApplicationViewSet):
    def get_serializer_class(self):
        return InnovationProjectSerializer
    
    def get_model(self):
        return InnovationProject
    
    def get_view_name(self):
        return "创新项目"


class CCFCSPCertificationViewSet(BaseApplicationViewSet):
    def get_serializer_class(self):
        return CCFCSPCertificationSerializer
    
    def get_model(self):
        return CCFCSPCertification
    
    def get_view_name(self):
        return "CCF-CSP认证"


class InternationalInternshipViewSet(BaseApplicationViewSet):
    def get_serializer_class(self):
        return InternationalInternshipSerializer
    
    def get_model(self):
        return InternationalInternship
    
    def get_view_name(self):
        return "国际实习"


class MilitaryServiceViewSet(BaseApplicationViewSet):
    def get_serializer_class(self):
        return MilitaryServiceSerializer
    
    def get_model(self):
        return MilitaryService
    
    def get_view_name(self):
        return "兵役服务"


class VolunteerServiceViewSet(BaseApplicationViewSet):
    def get_serializer_class(self):
        return VolunteerServiceSerializer
    
    def get_model(self):
        return VolunteerService
    
    def get_view_name(self):
        return "志愿服务"


class HonoraryTitleViewSet(BaseApplicationViewSet):
    def get_serializer_class(self):
        return HonoraryTitleSerializer
    
    def get_model(self):
        return HonoraryTitle
    
    def get_view_name(self):
        return "荣誉称号"


class SocialWorkViewSet(BaseApplicationViewSet):
    def get_serializer_class(self):
        return SocialWorkSerializer
    
    def get_model(self):
        return SocialWork
    
    def get_view_name(self):
        return "社会工作"


class SportsCompetitionViewSet(BaseApplicationViewSet):
    def get_serializer_class(self):
        return SportsCompetitionSerializer
    
    def get_model(self):
        return SportsCompetition
    
    def get_view_name(self):
        return "体育竞赛"


class ApplicationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        try:
            application_type = request.data.get('application_type')
            if not application_type:
                return Response({
                    'error': '缺少申请类型'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Map numeric application_type from frontend to string keys for backend
            type_mapping = {
                '1': 'english_score',
                '2': 'english_score',
                '3': 'academic_paper',
                '4': 'patent_work',
                '5': 'academic_competition',
                '6': 'innovation_project',
                '7': 'ccf_csp_certification',
                '8': 'international_internship',
                '9': 'military_service',
                '10': 'volunteer_service',
                '11': 'honorary_title',
                '12': 'social_work',
                '13': 'sports_competition',
                'english_score': 'english_score',
                'academic_paper': 'academic_paper',
                'patent_work': 'patent_work',
                'academic_competition': 'academic_competition',
                'innovation_project': 'innovation_project',
                'ccf_csp_certification': 'ccf_csp_certification',
                'international_internship': 'international_internship',
                'military_service': 'military_service',
                'volunteer_service': 'volunteer_service',
                'honorary_title': 'honorary_title',
                'social_work': 'social_work',
                'sports_competition': 'sports_competition',
            }
            
            application_type = type_mapping.get(str(application_type))
            if not application_type:
                return Response({'error': '无效的申请类型'}, status=status.HTTP_400_BAD_REQUEST)
            
            model_mapping = {
                'english_score': EnglishScore,
                'academic_paper': AcademicPaper,
                'patent_work': PatentWork,
                'academic_competition': AcademicCompetition,
                'innovation_project': InnovationProject,
                'ccf_csp_certification': CCFCSPCertification,
                'international_internship': InternationalInternship,
                'military_service': MilitaryService,
                'volunteer_service': VolunteerService,
                'honorary_title': HonoraryTitle,
                'social_work': SocialWork,
                'sports_competition': SportsCompetition,
            }
            
            # Create a mapping for create-specific serializers
            create_serializer_mapping = {
                'english_score': EnglishScoreCreateSerializer,
                'academic_paper': AcademicPaperCreateSerializer,
                'patent_work': PatentWorkCreateSerializer,
                'academic_competition': AcademicCompetitionCreateSerializer,
                'innovation_project': InnovationProjectCreateSerializer,
                'ccf_csp_certification': CCFCSPCertificationCreateSerializer,
                'international_internship': InternationalInternshipCreateSerializer,
                'military_service': MilitaryServiceCreateSerializer,
                'volunteer_service': VolunteerServiceCreateSerializer,
                'honorary_title': HonoraryTitleCreateSerializer,
                'social_work': SocialWorkCreateSerializer,
                'sports_competition': SportsCompetitionCreateSerializer,
            }
            
            serializer_class = create_serializer_mapping.get(application_type)
            if not serializer_class:
                return Response({'error': '无效的申请类型'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = serializer_class(data=request.data, context={'request': request})
            if serializer.is_valid():
                application = serializer.save(user=request.user)
                # 使用普通序列化器获取包含id的完整数据
                regular_serializer_class = {
                    'english_score': EnglishScoreSerializer,
                    'academic_paper': AcademicPaperSerializer,
                    'patent_work': PatentWorkSerializer,
                    'academic_competition': AcademicCompetitionSerializer,
                    'innovation_project': InnovationProjectSerializer,
                    'ccf_csp_certification': CCFCSPCertificationSerializer,
                    'international_internship': InternationalInternshipSerializer,
                    'military_service': MilitaryServiceSerializer,
                    'volunteer_service': VolunteerServiceSerializer,
                    'honorary_title': HonoraryTitleSerializer,
                    'social_work': SocialWorkSerializer,
                    'sports_competition': SportsCompetitionSerializer
                }[application_type]
                
                regular_serializer = regular_serializer_class(application, context={'request': request})
                return Response({
                    'success': True,
                    'message': '申请创建成功',
                    'data': regular_serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': '申请创建失败',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'申请创建失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        try:
            application_id = pk
            application_type = request.query_params.get('type') or request.data.get('application_type')
            
            if not application_type:
                return Response({'error': '缺少申请类型参数'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Map numeric application_type from frontend to string keys for backend
            type_mapping = {
                '1': 'english_score',
                '2': 'english_score',
                '3': 'academic_paper',
                '4': 'patent_work',
                '5': 'academic_competition',
                '6': 'innovation_project',
                '7': 'ccf_csp_certification',
                '8': 'international_internship',
                '9': 'military_service',
                '10': 'volunteer_service',
                '11': 'honorary_title',
                '12': 'social_work',
                '13': 'sports_competition',
                'english_score': 'english_score',
                'academic_paper': 'academic_paper',
                'patent_work': 'patent_work',
                'academic_competition': 'academic_competition',
                'innovation_project': 'innovation_project',
                'ccf_csp_certification': 'ccf_csp_certification',
                'international_internship': 'international_internship',
                'military_service': 'military_service',
                'volunteer_service': 'volunteer_service',
                'honorary_title': 'honorary_title',
                'social_work': 'social_work',
                'sports_competition': 'sports_competition',
            }
            
            application_type = type_mapping.get(str(application_type))
            if not application_type:
                return Response({'error': '无效的申请类型'}, status=status.HTTP_400_BAD_REQUEST)
            
            model_mapping = {
                'english_score': EnglishScore,
                'academic_paper': AcademicPaper,
                'patent_work': PatentWork,
                'academic_competition': AcademicCompetition,
                'innovation_project': InnovationProject,
                'ccf_csp_certification': CCFCSPCertification,
                'international_internship': InternationalInternship,
                'military_service': MilitaryService,
                'volunteer_service': VolunteerService,
                'honorary_title': HonoraryTitle,
                'social_work': SocialWork,
                'sports_competition': SportsCompetition,
            }
            
            serializer_class_mapping = {
                'english_score': EnglishScoreSerializer,
                'academic_paper': AcademicPaperSerializer,
                'patent_work': PatentWorkSerializer,
                'academic_competition': AcademicCompetitionSerializer,
                'innovation_project': InnovationProjectSerializer,
                'ccf_csp_certification': CCFCSPCertificationSerializer,
                'international_internship': InternationalInternshipSerializer,
                'military_service': MilitaryServiceSerializer,
                'volunteer_service': VolunteerServiceSerializer,
                'honorary_title': HonoraryTitleSerializer,
                'social_work': SocialWorkSerializer,
                'sports_competition': SportsCompetitionSerializer,
            }
            
            model = model_mapping.get(application_type)
            if not model:
                return Response({'error': '无效的申请类型'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                application = model.objects.get(id=application_id, user=request.user)
            except model.DoesNotExist:
                return Response({'error': '申请不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            serializer_class = serializer_class_mapping.get(application_type)
            if not serializer_class:
                return Response({'error': '无效的申请类型'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = serializer_class(application, data=request.data, context={'request': request}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': '申请更新成功',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': '申请更新失败',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'申请更新失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        try:
            application_id = pk
            user = request.user
            
            # 定义所有申请模型
            application_models = [
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
                SportsCompetition,
            ]
            
            # 遍历所有模型查找对应的申请
            application = None
            for model in application_models:
                try:
                    application = model.objects.get(id=application_id, user=user)
                    break
                except model.DoesNotExist:
                    continue
            
            if not application:
                return Response({'error': '申请不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            if application.review_status not in ['pending', 'first_reviewing', 'first_approved', 'second_reviewing', 'second_approved', 'third_reviewing']:
                return Response({'error': '当前状态的申请不可撤回'}, status=status.HTTP_400_BAD_REQUEST)
            
            application.review_status = 'withdrawn'
            application.save()
            
            return Response({
                'success': True,
                'message': '申请已成功撤回'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': f'撤回申请失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def types(self, request):
        try:
            application_types = [
                {'value': 'english_score', 'label': '英语成绩'},
                {'value': 'academic_paper', 'label': '学术论文'},
                {'value': 'patent_work', 'label': '专利著作'},
                {'value': 'academic_competition', 'label': '学业竞赛'},
                {'value': 'innovation_project', 'label': '大创项目'},
                {'value': 'ccf_csp_certification', 'label': 'CCF CSP认证'},
                {'value': 'international_internship', 'label': '国际组织实习'},
                {'value': 'military_service', 'label': '参军入伍'},
                {'value': 'volunteer_service', 'label': '志愿服务'},
                {'value': 'honorary_title', 'label': '荣誉称号'},
                {'value': 'social_work', 'label': '社会工作'},
                {'value': 'sports_competition', 'label': '体育比赛'},
            ]
            return Response(application_types, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': f'获取申请类型失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def application_stats(self, request):
        try:
            user = request.user
            
            # 根据用户类型确定查询范围
            if user.user_type == 'student':
                # 学生只能查看自己的申请统计
                query_filter = {'user': user}
                is_teacher = False
            elif user.user_type in ['teacher', 'admin']:
                # 教师只能看到自己学院的学生申请统计
                # 管理员可以看到所有申请统计
                query_filter = {}
                is_teacher = True
                
                # 教师权限过滤：只能看到所属学院的学生申请统计
                if user.user_type == 'teacher':
                    query_filter['user__college'] = user.college
            else:
                return Response(
                    {"error": "只有学生、教师和管理员可以查看申请统计"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            stats = {}
            models = [
                ('english_scores', EnglishScore),
                ('academic_papers', AcademicPaper),
                ('patent_works', PatentWork),
                ('academic_competitions', AcademicCompetition),
                ('innovation_projects', InnovationProject),
                ('ccf_csp_certifications', CCFCSPCertification),
                ('international_internships', InternationalInternship),
                ('military_services', MilitaryService),
                ('volunteer_services', VolunteerService),
                ('honorary_titles', HonoraryTitle),
                ('social_works', SocialWork),
                ('sports_competitions', SportsCompetition),
            ]
            
            total_applications = 0
            pending_applications = 0
            approved_applications = 0
            rejected_applications = 0
            withdrawn_applications = 0
            
            # 为教师用户重新初始化统计变量，因为需要特殊计算
            if is_teacher and user.user_type == 'teacher':
                pending_applications = 0
                approved_applications = 0
                rejected_applications = 0
                total_applications = 0
                withdrawn_applications = 0
            
            for model_name, model in models:
                queryset = model.objects.filter(**query_filter)
                
                # 基础统计
                base_stats = {
                    'total': queryset.count(),
                    'pending': queryset.filter(review_status='pending').count(),
                    'approved': queryset.filter(review_status__in=['approved', 'first_approved', 'second_approved']).count(),
                    'rejected': queryset.filter(review_status__in=['rejected', 'first_rejected', 'second_rejected', 'third_rejected']).count(),
                    'withdrawn': queryset.filter(review_status='withdrawn').count()
                }
                
                # 对于教师用户，需要重新计算待审批和已通过的数量
                if is_teacher and user.user_type == 'teacher':
                    # 待审批申请数量：所有该教师没有审批过的申请
                    # 这里的逻辑是：所有本学院的申请中，排除掉该教师已经审批过的申请
                    # 即该教师没有参与过任何审核阶段的申请
                    pending_count = 0
                    approved_count = 0
                    rejected_count = 0
                    total_count = 0
                    withdrawn_count = 0
                    
                    # 遍历所有申请，逐个检查
                    for application in queryset.all():
                        # 统计总数量和已撤回数量
                        total_count += 1
                        if application.review_status == 'withdrawn':
                            withdrawn_count += 1
                            continue
                        
                        # 检查该教师是否已经审批过该申请
                        is_reviewed_by_teacher = False
                        if hasattr(application, 'first_reviewer') and application.first_reviewer == user:
                            is_reviewed_by_teacher = True
                        elif hasattr(application, 'second_reviewer') and application.second_reviewer == user:
                            is_reviewed_by_teacher = True
                        elif hasattr(application, 'third_reviewer') and application.third_reviewer == user:
                            is_reviewed_by_teacher = True
                        
                        # 如果该教师没有审批过，计入待审批数量
                        if not is_reviewed_by_teacher:
                            pending_count += 1
                        else:
                            # 如果该教师审批过，根据状态计入已通过或已拒绝数量
                            if application.review_status in ['approved', 'first_approved', 'second_approved']:
                                approved_count += 1
                            elif application.review_status in ['rejected', 'first_rejected', 'second_rejected', 'third_rejected']:
                                rejected_count += 1
                    
                    # 更新统计数据
                    pending_applications += pending_count
                    approved_applications += approved_count
                    rejected_applications += rejected_count
                    total_applications += total_count
                    withdrawn_applications += withdrawn_count
                    
                    # 更新模型的统计数据
                    stats[model_name] = {
                        'total': total_count,
                        'pending': pending_count,
                        'approved': approved_count,
                        'rejected': rejected_count,
                        'withdrawn': withdrawn_count
                    }
                else:
                    # 对于学生和管理员，使用基础统计
                    total_applications += base_stats['total']
                    pending_applications += base_stats['pending']
                    approved_applications += base_stats['approved']
                    rejected_applications += base_stats['rejected']
                    withdrawn_applications += base_stats['withdrawn']
                    
                    stats[model_name] = base_stats
            
            # 准备返回数据
            response_data = {
                'success': True,
                'data': {
                    'total_applications': total_applications,
                    'pending_applications': pending_applications,
                    'approved_applications': approved_applications,
                    'rejected_applications': rejected_applications,
                    'withdrawn_applications': withdrawn_applications,
                    'application_stats': stats
                }
            }
            
            # 为教师和管理员添加前端期望的字段格式
            if is_teacher:
                # 统计管理的学生数量
                from user.models import User
                total_students = User.objects.filter(user_type='student').count()
                
                # 添加前端期望的字段格式
                response_data['data']['pending'] = pending_applications
                response_data['data']['pending_count'] = pending_applications
                response_data['data']['pending_count'] = pending_applications
                response_data['data']['approved'] = approved_applications
                response_data['data']['approved_count'] = approved_applications
                response_data['data']['approved_count'] = approved_applications
                response_data['data']['rejected'] = rejected_applications
                response_data['data']['rejected_count'] = rejected_applications
                response_data['data']['rejected_count'] = rejected_applications
                response_data['data']['total'] = total_applications
                response_data['data']['totalStudents'] = total_students
                response_data['data']['total_students'] = total_students
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': f'获取统计数据失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminMaterialApplicationViewSet(viewsets.ViewSet):
    """管理员材料申请视图集"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """获取所有申请列表（管理员/教师）"""
        user = request.user
        
        # 权限检查
        if not hasattr(user, 'user_type') or user.user_type not in ['teacher', 'admin']:
            return Response({
                "error": "只有教师和管理员可以查看所有申请"
            }, status=status.HTTP_403_FORBIDDEN)
        
        applications = []
        
        application_models = [
            (EnglishScore, 'english_scores'),
            (AcademicPaper, 'academic_papers'),
            (PatentWork, 'patent_works'),
            (AcademicCompetition, 'academic_competitions'),
            (InnovationProject, 'innovation_projects'),
            (CCFCSPCertification, 'ccf_csp_certifications'),
            (InternationalInternship, 'international_internships'),
            (MilitaryService, 'military_services'),
            (VolunteerService, 'volunteer_services'),
            (HonoraryTitle, 'honorary_titles'),
            (SocialWork, 'social_works'),
            (SportsCompetition, 'sports_competitions'),
        ]
        
        # 获取查询参数
        status_filter = request.query_params.get('status')
        search = request.query_params.get('search')
        project_types = request.query_params.getlist('project_types')
        
        # 项目类型映射：前端项目类型 -> 后端模型名称（支持中英文）
        project_type_mapping = {
            # 英文项目类型
            'english': 'english_scores',
            'english_cet4': 'english_scores',
            'english_cet6': 'english_scores',
            'academic_paper': 'academic_papers',
            'patent_work': 'patent_works',
            'academic_competition': 'academic_competitions',
            'innovation_project': 'innovation_projects',
            'ccf_csp': 'ccf_csp_certifications',
            'international_internship': 'international_internships',
            'military_service': 'military_services',
            'volunteer_service': 'volunteer_services',
            'honorary_title': 'honorary_titles',
            'social_work': 'social_works',
            'sports_competition': 'sports_competitions',
            # 中文项目类型
            '英语成绩': 'english_scores',
            '大学英语四级': 'english_scores',
            '大学英语六级': 'english_scores',
            '学术论文': 'academic_papers',
            '专利著作': 'patent_works',
            '学业竞赛': 'academic_competitions',
            '大创项目': 'innovation_projects',
            'CCF CSP认证': 'ccf_csp_certifications',
            '国际组织实习': 'international_internships',
            '参军入伍': 'military_services',
            '志愿服务': 'volunteer_services',
            '荣誉称号': 'honorary_titles',
            '社会工作': 'social_works',
            '体育比赛': 'sports_competitions'
        }
        
        # 应用项目类型过滤
        filtered_application_models = []
        if project_types and project_types != ['']:
            # 如果提供了项目类型参数，只保留匹配的模型
            for model, model_name in application_models:
                # 将模型名称映射到前端项目类型
                for project_type in project_types:
                    if project_type_mapping.get(project_type) == model_name:
                        filtered_application_models.append((model, model_name))
                        break
        else:
            # 否则使用所有模型
            filtered_application_models = application_models
        
        for model, model_name in filtered_application_models:
            # 基础查询
            queryset = model.objects.all().order_by('-created_at')
            
            # 教师权限过滤：只能看到所属学院的学生申请
            if user.user_type == 'teacher':
                # 只能看到自己学院的学生申请
                queryset = queryset.filter(user__college=user.college)
                
                # 根据不同状态应用不同的过滤逻辑
                if status_filter and status_filter != 'all':
                    # 已通过状态：只显示当前教师通过的申请
                    if status_filter == 'approved':
                        # 只显示当前教师审批通过的申请
                        queryset = queryset.filter(
                            # 一审通过且是当前教师审核
                            (models.Q(review_status='first_approved') & models.Q(first_reviewer=user)) |
                            # 二审通过且是当前教师审核
                            (models.Q(review_status='second_approved') & models.Q(second_reviewer=user)) |
                            # 最终通过且是当前教师审核
                            (models.Q(review_status='approved') & (
                                models.Q(first_reviewer=user) | 
                                models.Q(second_reviewer=user) |
                                models.Q(third_reviewer=user)
                            ))
                        )
                    # 已拒绝状态：显示所有已拒绝的申请（不需要是当前教师审核的）
                    elif status_filter == 'rejected':
                        queryset = queryset.filter(
                            review_status__in=['rejected', 'first_rejected', 'second_rejected', 'third_rejected']
                        )
                    # 待审核状态：显示需要当前教师审核的申请（不需要已经是审核人）
                    # 对于待审核状态，只需要是本学院的学生申请即可
                    elif status_filter == 'pending':
                        queryset = queryset.filter(
                            review_status__in=['pending', 'first_reviewing', 'second_reviewing', 'third_reviewing']
                        )
                    # 其他具体状态：显示匹配状态的申请
                    else:
                        queryset = queryset.filter(review_status=status_filter)
                # 当没有状态筛选或状态为'all'时，显示所有本学院的申请
                else:
                    # 不需要额外的审核人过滤，已经有学院过滤
                    pass
            # 管理员不需要额外的状态过滤，已经在上面处理了
            elif user.user_type == 'admin' and status_filter and status_filter != 'all':
                queryset = queryset.filter(review_status=status_filter)
            
            # 搜索筛选
            if search:
                # 尝试根据不同模型的字段进行搜索
                if model_name == 'english_scores':
                    queryset = queryset.filter(
                        Q(user__name__icontains=search) |
                        Q(user__school_id__icontains=search) |
                        Q(level__icontains=search)
                    )
                elif model_name == 'academic_papers':
                    queryset = queryset.filter(
                        Q(user__name__icontains=search) |
                        Q(user__school_id__icontains=search) |
                        Q(paper_title__icontains=search) |
                        Q(paper_doi__icontains=search)
                    )
                elif model_name == 'patent_works':
                    queryset = queryset.filter(
                        Q(user__name__icontains=search) |
                        Q(user__school_id__icontains=search) |
                        Q(patent_number__icontains=search)
                    )
                elif model_name == 'academic_competitions':
                    queryset = queryset.filter(
                        Q(user__name__icontains=search) |
                        Q(user__school_id__icontains=search) |
                        Q(competition_name__icontains=search) |
                        Q(competition_specific_name__icontains=search)
                    )
                else:
                    # 通用搜索字段
                    queryset = queryset.filter(
                        Q(user__name__icontains=search) |
                        Q(user__school_id__icontains=search)
                    )
            
            for application in queryset:
                project_name = ""
                if model_name == 'english_scores':
                    project_name = f"{application.get_exam_type_display()}"
                elif model_name == 'academic_papers':
                    project_name = application.paper_title or "学术论文加分申请"
                elif model_name == 'patent_works':
                    project_name = application.paper_title or "专利著作加分申请"
                elif model_name == 'academic_competitions':
                    project_name = application.competition_specific_name or application.competition_name or "学业竞赛加分申请"
                elif model_name == 'innovation_projects':
                    project_name = application.project_name or "创新项目加分申请"
                elif model_name == 'ccf_csp_certifications':
                    project_name = f"CCF CSP认证_{application.score}"
                elif model_name == 'international_internships':
                    project_name = application.organization_name or "国际实习加分申请"
                elif model_name == 'military_services':
                    project_name = f"参军入伍服兵役加分申请_一年以上两年以内"
                elif model_name == 'volunteer_services':
                    project_name = application.activity_name or "志愿服务加分申请"
                elif model_name == 'honorary_titles':
                    project_name = application.title_name or "荣誉称号加分申请"
                elif model_name == 'social_works':
                    project_name = application.organization or "社会工作加分申请"
                elif model_name == 'sports_competitions':
                    project_name = application.competition_name or "体育竞赛加分申请"
                
                attachments = collect_attachments(application, model)
                
                # Map category to correct type names for front-end display
                category_map = {
                    'english_scores': 'english',
                    'academic_papers': 'academic_paper',
                    'patent_works': 'patent_work',
                    'academic_competitions': 'academic_competition',
                    'innovation_projects': 'innovation',
                    'ccf_csp_certifications': 'ccf_csp',
                    'international_internships': 'internship',
                    'military_services': 'military',
                    'volunteer_services': 'volunteer_service',
                    'honorary_titles': 'honor',
                    'social_works': 'social',
                    'sports_competitions': 'sports_competition'
                }
                category = category_map[model_name]
                
                # 获取学生班级信息
                class_name = "未知"
                if hasattr(application.user, 'class_name') and application.user.class_name:
                    class_name = application.user.class_name
                elif hasattr(application.user, 'clazz') and application.user.clazz:
                    class_name = application.user.clazz.name
                elif hasattr(application.user, 'class_field') and application.user.class_field:
                    class_name = application.user.class_field
                
                # 获取项目类型的中文显示名称
                project_type_display = category_map[model_name]
                
                # 检查当前教师是否已审核该申请
                reviewedByCurrentTeacher = False
                if hasattr(application, 'first_reviewer') and application.first_reviewer == user:
                    reviewedByCurrentTeacher = True
                elif hasattr(application, 'second_reviewer') and application.second_reviewer == user:
                    reviewedByCurrentTeacher = True
                elif hasattr(application, 'third_reviewer') and application.third_reviewer == user:
                    reviewedByCurrentTeacher = True
                
                applications.append({
                    "id": str(application.id),
                    "category": category,
                    "title": project_name,
                    "score": getattr(application, 'estimated_score', 0) or 0,
                    "created_at": application.created_at.isoformat(),  # 申请时间，ISO格式便于前端处理
                    "applyTime": application.created_at.strftime("%Y-%m-%d %H:%M:%S"),  # 前端期望的申请时间格式
                    "review_status": application.review_status,
                    "attachments": attachments,
                    "student_name": application.user.name,
                    "student_id": application.user.school_id,
                    "application_type": model_name,
                    "class_name": class_name,  # 班级名称
                    "project_type": project_type_display,  # 项目类型
                    "type": project_type_display,  # 另一个可能的项目类型字段名
                    "className": class_name,  # 前端期望的班级名称字段名
                    "reviewedByCurrentTeacher": reviewedByCurrentTeacher  # 当前教师是否已审核该申请
                })
        
        # 分页
        page_size = int(request.query_params.get('page_size', 10))
        page = int(request.query_params.get('page', 1))
        
        start = (page - 1) * page_size
        end = start + page_size
        paginated_applications = applications[start:end]
        
        return Response({
            "success": True,
            "count": len(applications),
            "results": paginated_applications
        })
    
    def retrieve(self, request, pk=None):
        """获取申请详情（教师/管理员）"""
        user = request.user
        
        # 权限检查
        if not hasattr(user, 'user_type') or user.user_type not in ['teacher', 'admin']:
            return Response({
                "error": "只有教师和管理员可以查看申请详情"
            }, status=status.HTTP_403_FORBIDDEN)
        
        application_id = pk
        application = None
        model = None
        model_name = None
        
        # 支持的申请模型列表
        application_models = [
            (EnglishScore, 'english_scores'),
            (AcademicPaper, 'academic_papers'),
            (PatentWork, 'patent_works'),
            (AcademicCompetition, 'academic_competitions'),
            (InnovationProject, 'innovation_projects'),
            (CCFCSPCertification, 'ccf_csp_certifications'),
            (InternationalInternship, 'international_internships'),
            (MilitaryService, 'military_services'),
            (VolunteerService, 'volunteer_services'),
            (HonoraryTitle, 'honorary_titles'),
            (SocialWork, 'social_works'),
            (SportsCompetition, 'sports_competitions'),
        ]
        
        # 自动尝试通过id查找申请
        for model_candidate, name_candidate in application_models:
            try:
                application = model_candidate.objects.get(id=application_id)
                model = model_candidate
                model_name = name_candidate
                break
            except model_candidate.DoesNotExist:
                continue
        
        if not application:
            return Response({
                "error": "申请不存在"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 教师只能查看本学院学生的申请详情
        if user.user_type == 'teacher' and application.user.college != user.college:
            return Response({
                "error": "您只能查看本学院学生的申请详情"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 获取项目名称
        project_name = ""
        if model_name == 'english_scores':
            project_name = f"{application.get_exam_type_display()}"
        elif model_name == 'academic_papers':
            project_name = application.paper_title or "学术论文加分申请"
        elif model_name == 'patent_works':
            project_name = application.paper_title or "专利著作加分申请"
        elif model_name == 'academic_competitions':
            project_name = application.competition_specific_name or application.competition_name or "学业竞赛加分申请"
        elif model_name == 'innovation_projects':
            project_name = application.project_name or "创新项目加分申请"
        elif model_name == 'ccf_csp_certifications':
            project_name = f"CCF CSP认证_{application.score}"
        elif model_name == 'international_internships':
            project_name = application.organization_name or "国际实习加分申请"
        elif model_name == 'military_services':
            project_name = f"参军入伍服兵役加分申请_一年以上两年以内"
        elif model_name == 'volunteer_services':
            project_name = application.activity_name or "志愿服务加分申请"
        elif model_name == 'honorary_titles':
            project_name = application.title_name or "荣誉称号加分申请"
        elif model_name == 'social_works':
            project_name = application.organization or "社会工作加分申请"
        elif model_name == 'sports_competitions':
            project_name = application.competition_name or "体育竞赛加分申请"
        
        # 收集附件
        attachments = collect_attachments(application, model)
        
        # Map category to correct type names for front-end display
        category_map = {
            'english_scores': 'english',
            'academic_papers': 'academic_paper',
            'patent_works': 'patent_work',
            'academic_competitions': 'academic_competition',
            'innovation_projects': 'innovation',
            'ccf_csp_certifications': 'ccf_csp',
            'international_internships': 'internship',
            'military_services': 'military',
            'volunteer_services': 'volunteer_service',
            'honorary_titles': 'honor',
            'social_works': 'social',
            'sports_competitions': 'sports_competition'
        }
        category = category_map[model_name]
        
        # 获取学生班级信息
        class_name = "未知"
        if hasattr(application.user, 'class_name') and application.user.class_name:
            class_name = application.user.class_name
        elif hasattr(application.user, 'clazz') and application.user.clazz:
            class_name = application.user.clazz.name
        elif hasattr(application.user, 'class_field') and application.user.class_field:
            class_name = application.user.class_field
        
        # 构建响应数据
        response_data = {
            "success": True,
            "data": {
                "id": str(application.id),
                "category": category,
                "title": project_name,
                "score": getattr(application, 'estimated_score', 0) or 0,
                "created_at": application.created_at.isoformat(),
                "applyTime": application.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "review_status": application.review_status,
                "attachments": attachments,
                "student_name": application.user.name,
                "student_id": application.user.school_id,
                "application_type": model_name,
                "class_name": class_name,
                "project_type": category,
                "type": category,
                "className": class_name,
                "description": getattr(application, 'description', '') or getattr(application, 'user_explanation', '') or "无"
            }
        }
        
        return Response(response_data)
    
    @action(detail=False, methods=['get'])
    def recent_applications(self, request):
        """获取最近申请列表（教师/管理员）"""
        user = request.user
        
        # 权限检查
        if not hasattr(user, 'user_type') or user.user_type not in ['teacher', 'admin']:
            return Response({
                "error": "只有教师和管理员可以查看最近申请"
            }, status=status.HTTP_403_FORBIDDEN)
        
        applications = []
        
        application_models = [
            (EnglishScore, 'english_scores'),
            (AcademicPaper, 'academic_papers'),
            (PatentWork, 'patent_works'),
            (AcademicCompetition, 'academic_competitions'),
            (InnovationProject, 'innovation_projects'),
            (CCFCSPCertification, 'ccf_csp_certifications'),
            (InternationalInternship, 'international_internships'),
            (MilitaryService, 'military_services'),
            (VolunteerService, 'volunteer_services'),
            (HonoraryTitle, 'honorary_titles'),
            (SocialWork, 'social_works'),
            (SportsCompetition, 'sports_competitions'),
        ]
        
        # 获取查询参数
        page_size = int(request.query_params.get('page_size', 5))
        
        for model, model_name in application_models:
            # 过滤掉已撤回的申请 - 使用exclude代替ne查找（Django 5.2不再支持CharField的ne查找）
            queryset = model.objects.exclude(review_status='withdrawn').order_by('-created_at')[:page_size]
            
            for application in queryset:
                project_name = ""
                if model_name == 'english_scores':
                    project_name = f"{application.get_exam_type_display()}"
                elif model_name == 'academic_papers':
                    project_name = application.paper_title or "学术论文加分申请"
                elif model_name == 'patent_works':
                    project_name = application.paper_title or "专利著作加分申请"
                elif model_name == 'academic_competitions':
                    project_name = application.competition_specific_name or application.competition_name or "学业竞赛加分申请"
                elif model_name == 'innovation_projects':
                    project_name = application.project_name or "创新项目加分申请"
                elif model_name == 'ccf_csp_certifications':
                    project_name = f"CCF CSP认证_{application.score}"
                elif model_name == 'international_internships':
                    project_name = application.organization_name or "国际实习加分申请"
                elif model_name == 'military_services':
                    project_name = f"参军入伍服兵役加分申请_一年以上两年以内"
                elif model_name == 'volunteer_services':
                    project_name = application.activity_name or "志愿服务加分申请"
                elif model_name == 'honorary_titles':
                    project_name = application.title_name or "荣誉称号加分申请"
                elif model_name == 'social_works':
                    project_name = application.organization or "社会工作加分申请"
                elif model_name == 'sports_competitions':
                    project_name = application.competition_name or "体育竞赛加分申请"
                
                # 收集附件
                attachments = collect_attachments(application, model)
                
                # Map category to correct type names for front-end display
                category_map = {
                    'english_scores': 'english',
                    'academic_papers': 'academic_paper',
                    'patent_works': 'patent_work',
                    'academic_competitions': 'academic_competition',
                    'innovation_projects': 'innovation',
                    'ccf_csp_certifications': 'ccf_csp',
                    'international_internships': 'internship',
                    'military_services': 'military',
                    'volunteer_services': 'volunteer_service',
                    'honorary_titles': 'honor',
                    'social_works': 'social',
                    'sports_competitions': 'sports_competition'
                }
                category = category_map[model_name]
                
                # 获取学生班级信息
                class_name = "未知"
                if hasattr(application.user, 'class_name') and application.user.class_name:
                    class_name = application.user.class_name
                elif hasattr(application.user, 'clazz') and application.user.clazz:
                    class_name = application.user.clazz.name
                elif hasattr(application.user, 'class_field') and application.user.class_field:
                    class_name = application.user.class_field
                
                applications.append({
                    "id": str(application.id),
                    "category": category,
                    "title": project_name,
                    "score": getattr(application, 'estimated_score', 0) or 0,
                    "created_at": application.created_at.isoformat(),
                    "applyDate": application.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "applyTime": application.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "review_status": application.review_status,
                    "attachments": attachments,
                    "student_name": application.user.name,
                    "student_id": application.user.school_id,
                    "application_type": model_name,
                    "class_name": class_name,
                    "project_type": category,
                    "type": category,
                    "className": class_name
                })
        
        # 按创建时间排序
        applications.sort(key=lambda x: x['applyDate'], reverse=True)
        
        # 取前N条
        recent_applications = applications[:page_size]
        
        return Response({
            "success": True,
            "results": recent_applications
        })
    
    @action(detail=True, methods=['post'])    
    def approve(self, request, pk=None):
        """批准申请（支持三级审核）"""
        user = request.user
        
        # 权限检查
        if not hasattr(user, 'user_type') or user.user_type not in ['teacher', 'admin']:
            return Response({
                "error": "只有教师和管理员可以批准申请"
            }, status=status.HTTP_403_FORBIDDEN)
        
        application_id = pk
        application = None
        model = None
        
        # 支持的申请模型列表
        application_models = [
            (EnglishScore, 'english_scores'),
            (AcademicPaper, 'academic_papers'),
            (PatentWork, 'patent_works'),
            (AcademicCompetition, 'academic_competitions'),
            (InnovationProject, 'innovation_projects'),
            (CCFCSPCertification, 'ccf_csp_certifications'),
            (InternationalInternship, 'international_internships'),
            (MilitaryService, 'military_services'),
            (VolunteerService, 'volunteer_services'),
            (HonoraryTitle, 'honorary_titles'),
            (SocialWork, 'social_works'),
            (SportsCompetition, 'sports_competitions'),
        ]
        
        # 自动尝试通过id查找申请
        for model_candidate, name_candidate in application_models:
            try:
                application = model_candidate.objects.get(id=application_id)
                model = model_candidate
                break
            except model_candidate.DoesNotExist:
                continue
        
        if not application:
            return Response({
                "error": "申请不存在"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 获取审批分数
        score = request.data.get('score')
        
        # 如果没有提供分数，计算默认分数为前几次审核分数的最低值
        if not score:
            # 获取前几次审核的分数
            previous_scores = []
            # 检查是否有一审分数
            if hasattr(application, 'first_review_score') and application.first_review_score:
                previous_scores.append(float(application.first_review_score))
            # 检查是否有二审分数
            if hasattr(application, 'second_review_score') and application.second_review_score:
                previous_scores.append(float(application.second_review_score))
            # 检查是否有三审分数
            if hasattr(application, 'third_review_score') and application.third_review_score:
                previous_scores.append(float(application.third_review_score))
            # 检查是否有bonus_points字段
            if hasattr(application, 'bonus_points') and application.bonus_points:
                previous_scores.append(float(application.bonus_points))
            # 检查是否有estimated_score字段
            if hasattr(application, 'estimated_score') and application.estimated_score:
                previous_scores.append(float(application.estimated_score))
            
            # 计算最低分数作为默认值
            if previous_scores:
                score = str(min(previous_scores))
            else:
                return Response({
                    "error": "缺少审批分数"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新申请状态和分数
        try:
            from django.utils import timezone
            
            # 检查教师是否已经审批过该申请
            has_reviewed = False
            if (hasattr(application, 'first_reviewer') and application.first_reviewer == user) or \
               (hasattr(application, 'second_reviewer') and application.second_reviewer == user) or \
               (hasattr(application, 'third_reviewer') and application.third_reviewer == user):
                has_reviewed = True
            
            # 允许教师修改自己的审核决定
            # if has_reviewed:
            #     return Response({
            #         "error": "您已经审批过该申请"
            #     }, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取审批分数和审核意见
            review_comment = request.data.get('review_comment', '')
            
            # 确保分数是数字类型
            try:
                bonus_points = float(score) if score is not None else None
            except (ValueError, TypeError):
                bonus_points = None
            
            # 检查教师是否已经审批过该申请
            is_first_reviewer = hasattr(application, 'first_reviewer') and application.first_reviewer == user
            is_second_reviewer = hasattr(application, 'second_reviewer') and application.second_reviewer == user
            is_third_reviewer = hasattr(application, 'third_reviewer') and application.third_reviewer == user
            
            # 获取当前审核阶段
            current_status = application.review_status
            
            # 根据当前状态和审核人身份执行相应的审核操作
            if current_status in ['pending', 'first_reviewing'] or is_first_reviewer:
                # 一审或修改一审决定
                if hasattr(application, 'perform_first_review'):
                    application.perform_first_review(user, 'passed', review_comment)
                else:
                    # 兼容旧模型，直接更新字段
                    application.first_reviewer = user
                    application.first_reviewed_at = timezone.now()
                    application.review_status = 'first_approved'
            elif current_status in ['first_approved', 'second_reviewing'] or is_second_reviewer:
                # 二审或修改二审决定
                if hasattr(application, 'perform_second_review'):
                    application.perform_second_review(user, 'passed', review_comment, bonus_points)
                else:
                    # 兼容旧模型，直接更新字段
                    application.second_reviewer = user
                    application.second_reviewed_at = timezone.now()
                    application.review_status = 'second_approved'
            elif current_status in ['second_approved', 'third_reviewing'] or is_third_reviewer:
                # 三审或修改三审决定
                if hasattr(application, 'perform_third_review'):
                    application.perform_third_review(user, 'passed', review_comment, bonus_points)
                else:
                    # 兼容旧模型，直接更新字段
                    application.third_reviewer = user
                    application.third_reviewed_at = timezone.now()
                    application.review_status = 'approved'
            elif current_status in ['rejected', 'first_rejected', 'second_rejected', 'third_rejected']:
                # 已拒绝的申请重新同意，进入一审通过状态
                if hasattr(application, 'perform_first_review'):
                    application.perform_first_review(user, 'passed', review_comment)
                else:
                    application.first_reviewer = user
                    application.first_reviewed_at = timezone.now()
                    application.review_status = 'first_approved'
            
            # 设置实际分数，根据模型类型使用不同的字段名
            if hasattr(application, 'bonus_points') and bonus_points is not None:
                application.bonus_points = bonus_points
            application.save()
            
            return Response({
                "success": True,
                "message": f"申请已成功{application.review_status}",
                "data": {
                    "new_status": application.review_status
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": f"批准申请失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """拒绝申请（支持三级审核）"""
        user = request.user
        
        # 权限检查
        if not hasattr(user, 'user_type') or user.user_type not in ['teacher', 'admin']:
            return Response({
                "error": "只有教师和管理员可以拒绝申请"
            }, status=status.HTTP_403_FORBIDDEN)
        
        application_id = pk
        application = None
        model = None
        
        # 支持的申请模型列表
        application_models = [
            (EnglishScore, 'english_scores'),
            (AcademicPaper, 'academic_papers'),
            (PatentWork, 'patent_works'),
            (AcademicCompetition, 'academic_competitions'),
            (InnovationProject, 'innovation_projects'),
            (CCFCSPCertification, 'ccf_csp_certifications'),
            (InternationalInternship, 'international_internships'),
            (MilitaryService, 'military_services'),
            (VolunteerService, 'volunteer_services'),
            (HonoraryTitle, 'honorary_titles'),
            (SocialWork, 'social_works'),
            (SportsCompetition, 'sports_competitions'),
        ]
        
        # 自动尝试通过id查找申请
        for model_candidate, name_candidate in application_models:
            try:
                application = model_candidate.objects.get(id=application_id)
                model = model_candidate
                break
            except model_candidate.DoesNotExist:
                continue
        
        if not application:
            return Response({
                "error": "申请不存在"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 获取拒绝理由
        reason = request.data.get('reason')
        if not reason:
            return Response({
                "error": "缺少拒绝理由"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新申请状态
        try:
            from django.utils import timezone
            
            # 任何一个老师拒绝，直接设置为最终拒绝状态
            reject_status = 'rejected'  # 任意老师拒绝，直接变为最终拒绝
            
            # 检查教师是否已经审批过该申请
            is_first_reviewer = hasattr(application, 'first_reviewer') and application.first_reviewer == user
            is_second_reviewer = hasattr(application, 'second_reviewer') and application.second_reviewer == user
            is_third_reviewer = hasattr(application, 'third_reviewer') and application.third_reviewer == user
            
            # 设置对应的审核人信息
            current_status = application.review_status
            if current_status in ['pending', 'first_reviewing'] or is_first_reviewer:
                # 一审拒绝或修改一审决定为拒绝
                application.first_reviewer = user
                application.first_reviewed_at = timezone.now()
            elif current_status in ['first_approved', 'second_reviewing'] or is_second_reviewer:
                # 二审拒绝或修改二审决定为拒绝
                application.second_reviewer = user
                application.second_reviewed_at = timezone.now()
            elif current_status in ['second_approved', 'third_reviewing'] or is_third_reviewer:
                # 三审拒绝或修改三审决定为拒绝
                application.third_reviewer = user
                application.third_reviewed_at = timezone.now()
            
            application.review_status = reject_status
            # 设置拒绝理由，根据模型类型和审核人身份使用不同的字段名
            if hasattr(application, 'rejection_reason'):
                application.rejection_reason = reason
            elif hasattr(application, 'review_notes'):
                application.review_notes = reason
            elif hasattr(application, 'first_review_comment') and (is_first_reviewer or current_status in ['pending', 'first_reviewing']):
                application.first_review_comment = reason
            elif hasattr(application, 'second_review_comment') and (is_second_reviewer or current_status in ['first_approved', 'second_reviewing']):
                application.second_review_comment = reason
            elif hasattr(application, 'third_review_comment') and (is_third_reviewer or current_status in ['second_approved', 'third_reviewing']):
                application.third_review_comment = reason
            application.save()
            
            return Response({
                "success": True,
                "message": f"申请已成功{reject_status}",
                "data": {
                    "new_status": reject_status
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": f"拒绝申请失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def upload_file(request):
    """
    文件上传视图
    接受multipart/form-data格式的文件上传请求
    返回包含文件URL的JSON响应
    """
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        # 生成唯一文件名，避免重名
        file_ext = uploaded_file.name.split('.')[-1]
        unique_filename = f"{uuid4()}.{file_ext}"
        
        # 确保上传目录存在
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, unique_filename)
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # 生成文件URL
        file_url = f"{settings.MEDIA_URL}uploads/{unique_filename}"
        
        # 返回响应
        return Response({'url': file_url}, status=status.HTTP_201_CREATED)
    
    return Response({'error': '无效的请求'}, status=status.HTTP_400_BAD_REQUEST)