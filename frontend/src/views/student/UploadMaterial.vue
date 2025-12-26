<template>
  <div class="upload-container">
    <h2 class="page-title">添加申请</h2>
    
    <a-card class="upload-card">
      <a-form
        :model="formData"
        :rules="formRules"
        ref="formRef"
        class="upload-form"
        layout="vertical"
        @finish="handleSubmit"
      >
        <!-- 大类选择 -->
        <a-form-item label="申请大类" name="projectCategory">
          <a-select
            v-model:value="formData.projectCategory"
            placeholder="请选择申请大类"
            @change="handleCategoryChange"
          >
            <a-select-option value="academic_excellence">学术专长成绩</a-select-option>
            <a-select-option value="comprehensive_performance">综合表现加分</a-select-option>
            <a-select-option value="english_cet">英语四六级成绩</a-select-option>
          </a-select>
        </a-form-item>

        <!-- 子类选择 -->
        <a-form-item v-if="formData.projectCategory" label="具体项目类型" name="projectType">
          <a-select
            v-model:value="formData.projectType"
            placeholder="请选择具体项目类型"
            @change="handleProjectTypeChange"
          >
            <!-- 学术专长成绩子类 -->
            <template v-if="formData.projectCategory === 'academic_excellence'">
              <a-select-option value="research_achievements">科研成果</a-select-option>
              <a-select-option value="academic_competition">学术竞赛</a-select-option>
              <a-select-option value="innovation_project">创新项目</a-select-option>
            </template>

            <!-- 综合表现加分子类 -->
            <template v-else-if="formData.projectCategory === 'comprehensive_performance'">
              <a-select-option value="international_internship">国际组织实习</a-select-option>
              <a-select-option value="military_service">参军入伍</a-select-option>
              <a-select-option value="volunteer_service">志愿服务</a-select-option>
              <a-select-option value="honorary_title">荣誉称号</a-select-option>
              <a-select-option value="social_work">社会工作</a-select-option>
              <a-select-option value="sports_competition">体育竞赛</a-select-option>
            </template>

            <!-- 英语四六级成绩子类 -->
            <template v-else-if="formData.projectCategory === 'english_cet'">
              <a-select-option value="english_cet4">英语四级</a-select-option>
              <a-select-option value="english_cet6">英语六级</a-select-option>
            </template>
          </a-select>
        </a-form-item>
        
        <!-- 科研成果子类型选择 -->
        <a-form-item v-if="formData.projectType === 'research_achievements'" label="科研成果类型" name="subProjectType">
          <a-select
            v-model:value="formData.subProjectType"
            placeholder="请选择科研成果类型"
            @change="handleSubProjectTypeChange"
          >
            <a-select-option value="academic_paper">学术论文</a-select-option>
            <a-select-option value="invention_patent">发明专利</a-select-option>
          </a-select>
        </a-form-item>
        
        <!-- 通用字段 -->
        <!-- 已移除冗余字段：申请标题、申请描述、个人说明 -->
        
        <!-- 学术论文特有字段 -->
        <template v-if="(formData.projectType === 'academic_paper' || formData.subProjectType === 'academic_paper')">
          <a-form-item label="论文标题" name="paper_title">
            <a-input
              v-model:value="formData.paper_title"
              placeholder="请输入论文标题"
              :maxlength="200"
              show-count
            />
            <div class="form-item-help">论文标题不能为空，长度不超过200字符</div>
          </a-form-item>
          
          <!-- 移除论文DOI字段 -->
          <!-- <a-form-item label="论文DOI" name="paper_doi">
            <a-input
              v-model:value="formData.paper_doi"
              placeholder="请输入论文DOI"
              :maxlength="100"
            />
            <div class="form-item-help">论文DOI是数字对象标识符，用于唯一标识学术论文，格式如：10.1234/test.doi</div>
          </a-form-item> -->
          
          <a-form-item label="期刊/会议分类" name="journal_category">
            <a-select
              v-model:value="formData.journal_category"
              placeholder="请选择期刊/会议分类"
            >
              <a-select-option value="nature_science_cell">Nature/Science/Cell主刊</a-select-option>
              <a-select-option value="nature_science_cell_sub">Nature/Science/Cell子刊 (IF≥10)</a-select-option>
              <a-select-option value="a_class">A类期刊/会议</a-select-option>
              <a-select-option value="b_class">B类期刊/会议</a-select-option>
              <a-select-option value="c_class">C类期刊/会议</a-select-option>
              <a-select-option value="high_level_chinese">高水平中文学术期刊</a-select-option>
              <a-select-option value="ict_recommended">信息与通信工程学科推荐国际学术期刊</a-select-option>
            </a-select>
            <div class="form-item-help">请选择与论文发表相关的期刊或会议分类</div>
          </a-form-item>
          
          <!-- 作者身份选项组 -->
          <a-form-item label="作者身份" required>
            <!-- 是否为独立作者 -->
            <a-radio-group v-model:value="formData.is_independent_author" button-style="solid" name="is_independent_author">
              <a-radio-button value="true">是</a-radio-button>
              <a-radio-button value="false">否</a-radio-button>
            </a-radio-group>
            <div class="form-item-help">独立作者：论文作者列表中只有申请人一人</div>
          </a-form-item>
          
          <!-- 若不是独立作者，显示是否为共同第一作者 -->
          <a-form-item v-if="formData.is_independent_author === 'false'" label="是否为共同第一作者" name="is_co_first_author">
            <a-radio-group v-model:value="formData.is_co_first_author" button-style="solid">
              <a-radio-button value="true">是</a-radio-button>
              <a-radio-button value="false">否</a-radio-button>
            </a-radio-group>
            <div class="form-item-help">共同第一作者：两位作者贡献相同，排名不分先后</div>
          </a-form-item>
          
          <!-- 若不是共同第一作者，显示作者排序 -->
          <a-form-item v-if="formData.is_independent_author === 'false' && formData.is_co_first_author === 'false'" label="作者排序" name="author_rank">
            <a-select v-model:value="formData.author_rank" placeholder="请选择作者排序">
              <a-select-option value="1">一</a-select-option>
              <a-select-option value="2">二</a-select-option>
            </a-select>
            <div class="form-item-help">选择您在论文作者列表中的排序位置</div>
          </a-form-item>
          
          <a-form-item label="厦门大学是否为第一单位" name="is_xmu_first_unit" :rules="[{ required: true, message: '请选择是否为第一单位', trigger: 'change' }, { validator: validateXmuFirstUnit, trigger: 'change' }]">
            <a-radio-group v-model:value="formData.is_xmu_first_unit" button-style="solid">
              <a-radio-button value="true">是</a-radio-button>
              <a-radio-button value="false">否</a-radio-button>
            </a-radio-group>
            <div class="form-item-help">厦门大学必须为第一单位，否则无法获得加分</div>
          </a-form-item>
        </template>
        
        <!-- 发明专利特有字段 -->
        <template v-if="formData.subProjectType === 'invention_patent'">
          <a-form-item label="专利名称" name="patent_title" :rules="[{ required: true, message: '请输入专利名称', trigger: 'blur' }]">
            <a-input
              v-model:value="formData.patent_title"
              placeholder="请输入专利名称"
              :maxlength="200"
              show-count
            />
            <div class="form-item-help">专利名称不能为空，长度不超过200字符</div>
          </a-form-item>
          
          <a-form-item label="作者类型" name="author_type" :rules="[{ required: true, message: '请选择作者类型', trigger: 'change' }]">
            <a-radio-group v-model:value="formData.author_type" button-style="solid">
              <a-radio-button value="first_author_except_teacher">除老师外第一作者</a-radio-button>
              <a-radio-button value="independent_author">独立作者</a-radio-button>
            </a-radio-group>
            <div class="form-item-help">请选择您在专利中的作者类型</div>
          </a-form-item>
          
          <a-form-item label="厦门大学是否为第一单位" name="is_xmu_first_unit" :rules="[{ required: true, message: '请选择是否为第一单位', trigger: 'change' }, { validator: validateXmuFirstUnit, trigger: 'change' }]">
            <a-radio-group v-model:value="formData.is_xmu_first_unit" button-style="solid">
              <a-radio-button value="true">是</a-radio-button>
              <a-radio-button value="false">否</a-radio-button>
            </a-radio-group>
            <div class="form-item-help">厦门大学必须为第一单位才能提交申请</div>
          </a-form-item>
        </template>
        
        <!-- 创新项目特有字段 -->
        <template v-if="formData.projectType === 'innovation_project'">
          <a-form-item label="项目名称" name="project_name">
            <a-input v-model:value="formData.project_name" placeholder="请输入项目名称" />
          </a-form-item>
          
          <a-form-item label="项目级别" name="project_level">
            <a-select v-model:value="formData.project_level" placeholder="请选择项目级别">
              <a-select-option value="national">国家级</a-select-option>
              <a-select-option value="provincial">省级</a-select-option>
              <a-select-option value="school">校级</a-select-option>
            </a-select>
          </a-form-item>
          
          <a-form-item label="是否为负责人" name="is_responsible_person">
            <a-radio-group v-model:value="formData.is_responsible_person">
              <a-radio value="true">是</a-radio>
              <a-radio value="false">否</a-radio>
            </a-radio-group>
          </a-form-item>
        </template>
        
        <!-- CCF CSP特有字段 -->
        <template v-if="formData.projectType === 'ccf_csp'">
          <a-form-item label="考试成绩" name="exam_score">
            <a-input-number
              v-model:value="formData.exam_score"
              :min="0"
              :max="100"
              :step="1"
              placeholder="请输入CCF CSP成绩"
            />
          </a-form-item>
          
          <a-form-item label="考试日期" name="exam_date">
            <a-date-picker
              v-model:value="formData.exam_date"
              placeholder="请选择考试日期"
              style="width: 100%"
            />
          </a-form-item>
        </template>
        
        <!-- 英语四六级特有字段 -->
        <template v-if="formData.projectType === 'english_cet4' || formData.projectType === 'english_cet6'">
          <a-form-item label="考试成绩" name="exam_score">
            <a-input-number
              v-model:value="formData.exam_score"
              :min="0"
              :max="710"
              :step="1"
              placeholder="请输入考试成绩"
            />
          </a-form-item>
        </template>
        
        <!-- 志愿服务特有字段 -->
        <template v-if="formData.projectType === 'volunteer_service'">
          <a-form-item label="服务类型" name="volunteer_service_type">
            <a-select v-model:value="formData.volunteer_service_type" placeholder="请选择服务类型">
              <a-select-option value="service_hours">志愿服务</a-select-option>
              <a-select-option value="recognition">志愿表彰</a-select-option>
            </a-select>
          </a-form-item>
          
          <!-- 志愿服务（时长）特有字段 -->
          <template v-if="formData.volunteer_service_type === 'service_hours'">
            <a-form-item label="服务时长(小时)" name="service_hours">
              <a-input-number
                v-model:value="formData.service_hours"
                :min="0"
                :step="0.5"
                placeholder="请输入服务时长"
              />
              <div class="form-item-help">累计登记的志愿服务时间达到200小时以上（含200小时）并得到认可，超过200小时后每增加2小时可增加0.05分。大型赛会志愿者与支教活动工时减半。该项最多加1分。</div>
            </a-form-item>
          </template>
          
          <!-- 志愿表彰特有字段 -->
          <template v-else-if="formData.volunteer_service_type === 'recognition'">
            <a-form-item label="表彰级别" name="recognition_level">
              <a-select v-model:value="formData.recognition_level" placeholder="请选择表彰级别">
                <a-select-option value="national">国家级</a-select-option>
                <a-select-option value="provincial">省级</a-select-option>
                <a-select-option value="school">校级</a-select-option>
              </a-select>
            </a-form-item>
            
            <a-form-item label="表彰类型" name="recognition_type">
              <a-radio-group v-model:value="formData.recognition_type">
                <a-radio value="team">团队</a-radio>
                <a-radio value="individual">个人</a-radio>
              </a-radio-group>
            </a-form-item>
            
            <!-- 团队表彰特有字段 -->
            <template v-if="formData.recognition_type === 'team'">
              <a-form-item label="在团队中的角色" name="team_role">
                <a-select v-model:value="formData.team_role" placeholder="请选择在团队中的角色">
                  <a-select-option value="captain">队长</a-select-option>
                  <a-select-option value="member">队员</a-select-option>
                </a-select>
              </a-form-item>
            </template>
            
            <div class="form-item-help">
              <p>志愿表彰加分标准：</p>
              <table class="score-table">
                <thead>
                  <tr>
                    <th>类型</th>
                    <th>角色</th>
                    <th>国家级</th>
                    <th>省级</th>
                    <th>校级</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>团队</td>
                    <td>队长</td>
                    <td>1分</td>
                    <td>0.5分</td>
                    <td>0.25分</td>
                  </tr>
                  <tr>
                    <td>团队</td>
                    <td>队员</td>
                    <td>0.5分</td>
                    <td>0.25分</td>
                    <td>0.1分</td>
                  </tr>
                  <tr>
                    <td>个人</td>
                    <td>-</td>
                    <td>1分</td>
                    <td>0.5分</td>
                    <td>0.25分</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </template>
        </template>
        
        <!-- 社会工作特有字段 -->
        <template v-if="formData.projectType === 'social_work'">
          <a-form-item label="职务名称" name="position_name">
            <a-input v-model:value="formData.position_name" placeholder="请输入职务名称" />
          </a-form-item>
          
          <a-form-item label="任期年数" name="term_years">
            <a-select v-model:value="formData.term_years" placeholder="请选择任期年数">
              <a-select-option value="0.5">超过一学期但不满一年</a-select-option>
              <a-select-option value="1">满一学年</a-select-option>
              <a-select-option value="2">两学年</a-select-option>
              <a-select-option value="3">三学年</a-select-option>
            </a-select>
          </a-form-item>
          
          <a-form-item label="老师打分" name="teacher_score">
            <a-input-number
              v-model:value="formData.teacher_score"
              :min="0"
              :max="100"
              :step="1"
              placeholder="请输入老师打分"
            />
          </a-form-item>
          
          <div class="form-item-help">
            <p>加分规则说明：</p>
            <table class="score-table">
              <thead>
                <tr>
                  <th>担任职务</th>
                  <th>系数</th>
                  <th>最终得分</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>院学生会执行主席、团总支书记</td>
                  <td>2</td>
                  <td>2*得分/100</td>
                </tr>
                <tr>
                  <td>院学生会主席团成员、团总支副书记</td>
                  <td>1.5</td>
                  <td>1.5*得分/100</td>
                </tr>
                <tr>
                  <td>院学生会、团总支各部部长，党支部书记，班长、团支部书记</td>
                  <td>1</td>
                  <td>1*得分/100</td>
                </tr>
                <tr>
                  <td>系团总支书记，院学生会、团总支各部门副部长，社团社长</td>
                  <td>0.75</td>
                  <td>0.75*得分/100</td>
                </tr>
                <tr>
                  <td>党支部委员，系团总支各部部长，各班班委、团支部委员，院学生会、团总支长期志愿者，社团副社长及社团主要干部、辩论队队长、球队队长等</td>
                  <td>0.5</td>
                  <td>0.5*得分/100</td>
                </tr>
              </tbody>
            </table>
            <p>注：1. 任期超过一学期但不满一年的按一学年标准减半计算，不满一个学期的不加分。</p>
            <p>2. 同一学年兼任多个学生干部职务的，只按照最高分值加分，不得累计加分。</p>
            <p>3. 不同学年担任学生干部可累加。该项最多加2分。</p>
          </div>
        </template>
        
        <!-- 荣誉称号验证规则 -->
        <template v-if="formData.projectType === 'honorary_title'">
          <a-form-item label="荣誉名称" name="honor_name">
            <a-input v-model:value="formData.honor_name" placeholder="请输入荣誉名称" />
          </a-form-item>
          
          <a-form-item label="荣誉级别" name="honor_level">
            <a-select v-model:value="formData.honor_level" placeholder="请选择荣誉级别">
              <a-select-option value="national">国家级</a-select-option>
              <a-select-option value="provincial">省级</a-select-option>
              <a-select-option value="school">校级</a-select-option>
            </a-select>
          </a-form-item>
          
          <a-form-item label="授予学年" name="awarding_year">
            <a-input-number
              v-model:value="formData.awarding_year"
              :min="2000"
              :max="new Date().getFullYear()"
              placeholder="请输入授予学年"
            />
            <div class="form-item-help">例如：2023</div>
          </a-form-item>
          
          <a-form-item label="是否是集体荣誉" name="is_collective">
            <a-radio-group v-model:value="formData.is_collective">
              <a-radio value="true">是</a-radio>
              <a-radio value="false">否</a-radio>
            </a-radio-group>
            <div class="form-item-help">集体荣誉称号加分，所在集体每位成员均可得分，得分减半</div>
          </a-form-item>
        </template>
        
        <!-- 体育竞赛特有字段 -->
        <template v-if="formData.projectType === 'sports_competition'">
          <a-form-item label="竞赛名称" name="competition_name">
            <a-input v-model:value="formData.competition_name" placeholder="请输入竞赛名称" />
          </a-form-item>
          
          <a-form-item label="竞赛级别" name="competition_level">
            <a-select v-model:value="formData.competition_level" placeholder="请选择竞赛级别">
              <a-select-option value="international">国际级</a-select-option>
              <a-select-option value="national">国家级</a-select-option>
              <a-select-option value="provincial">省级</a-select-option>
              <a-select-option value="school">校级</a-select-option>
            </a-select>
          </a-form-item>
          
          <a-form-item label="获奖等级" name="award_level">
            <a-select v-model:value="formData.award_level" placeholder="请选择获奖等级">
              <a-select-option value="champion">冠军</a-select-option>
              <a-select-option value="runner_up">亚军</a-select-option>
              <a-select-option value="third_place">季军</a-select-option>
              <a-select-option value="fourth_to_eighth">第四至八名</a-select-option>
            </a-select>
          </a-form-item>
          
          <a-form-item label="是否是团队项目" name="is_team_project">
            <a-radio-group v-model:value="formData.is_team_project">
              <a-radio value="true">是</a-radio>
              <a-radio value="false">否</a-radio>
            </a-radio-group>
          </a-form-item>
          
          <!-- 团队项目 -->
          <template v-if="formData.is_team_project === 'true'">
            <a-form-item label="团队成员数" name="team_size">
              <a-input-number
                v-model:value="formData.team_size"
                :min="2"
                :step="1"
                placeholder="请输入团队成员数"
              />
              <div class="form-item-help">团队成员数不小于2</div>
            </a-form-item>
          </template>
          
          <!-- 非团队项目 -->
          <template v-else>
            <a-form-item label="项目类型" name="project_type">
              <a-select v-model:value="formData.project_type" placeholder="请选择项目类型">
                <a-select-option value="individual">单人项目</a-select-option>
                <a-select-option value="two_person">二人项目</a-select-option>
              </a-select>
            </a-form-item>
          </template>
          
          <div class="form-item-help">
            <p>体育竞赛加分规则：</p>
            <table class="score-table">
              <thead>
                <tr>
                  <th>竞赛级别</th>
                  <th>获奖等级</th>
                  <th>团体项目加分</th>
                  <th>单人/二人项目加分</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td rowspan="8">国际级</td>
                  <td>冠军</td>
                  <td>8分</td>
                  <td>8/3分</td>
                </tr>
                <tr>
                  <td>亚军</td>
                  <td>6.5分</td>
                  <td>6.5/3分</td>
                </tr>
                <tr>
                  <td>季军</td>
                  <td>5分</td>
                  <td>5/3分</td>
                </tr>
                <tr>
                  <td>第四至八名</td>
                  <td>3.5分</td>
                  <td>3.5/3分</td>
                </tr>
                <tr>
                  <td>国家级</td>
                  <td>冠军</td>
                  <td>5分</td>
                  <td>5/3分</td>
                </tr>
                <tr>
                  <td>国家级</td>
                  <td>亚军</td>
                  <td>3.5分</td>
                  <td>3.5/3分</td>
                </tr>
                <tr>
                  <td>国家级</td>
                  <td>季军</td>
                  <td>2分</td>
                  <td>2/3分</td>
                </tr>
                <tr>
                  <td>国家级</td>
                  <td>第四至八名</td>
                  <td>1分</td>
                  <td>1/3分</td>
                </tr>
              </tbody>
            </table>
            <p>注：1. 团体项目获奖，参赛成员按参赛人数平均计算加分值。</p>
            <p>2. 二人项目或个人项目获奖，加分按同一级别团体项目获奖加分值的1/3计算。</p>
            <p>3. 同一赛事不同级别的比赛，只按照获奖最高级别或最高分值加分，不得累计加分。</p>
          </div>
        </template>
        
        <!-- 国际组织实习特有字段 -->
        <template v-if="formData.projectType === 'international_internship'">
          <a-form-item label="实习机构名称" name="institution_name">
            <a-input v-model:value="formData.institution_name" placeholder="请输入实习机构名称" />
          </a-form-item>
          
          <a-form-item label="实习时长类型" name="internship_duration_type">
            <a-select v-model:value="formData.internship_duration_type" placeholder="请选择实习时长类型">
              <a-select-option value="full_year">满一学年</a-select-option>
              <a-select-option value="half_year">满一学期</a-select-option>
            </a-select>
            <div class="form-item-help">满一学年得1分，满一学期得0.5分，不满一学期不得分</div>
          </a-form-item>
        </template>
        
        <!-- 参军入伍特有字段 -->
        <template v-if="formData.projectType === 'military_service'">
          <a-form-item label="服兵役时长" name="military_service_duration">
            <a-select v-model:value="formData.military_service_duration" placeholder="请选择服兵役时长">
              <a-select-option value="one_to_two_years">一年以上（含一年）、两年以内</a-select-option>
              <a-select-option value="two_years_plus">两年以上（含两年）</a-select-option>
            </a-select>
            <div class="form-item-help">一年以上（含一年）、两年以内的，加1分；两年以上（含两年）的加2分。该项最多加2分。</div>
          </a-form-item>
        </template>
        
        <!-- 学术竞赛特有字段 -->
        <template v-if="formData.projectType === 'academic_competition'">

          
          <a-form-item label="竞赛类型" name="competition_type">
            <a-radio-group v-model:value="formData.competition_type" button-style="solid" @change="handleCompetitionTypeChange">
              <a-radio-button value="competition">竞赛</a-radio-button>
              <a-radio-button value="csp">CCF CSP认证</a-radio-button>
            </a-radio-group>
            <div class="form-item-help">请选择竞赛类型</div>
          </a-form-item>
          
          <!-- 普通竞赛表单 -->
          <template v-if="formData.competition_type === 'competition'">

          
          <a-form-item label="竞赛名称" name="competition_name">
            <a-input
              v-model:value="formData.competition_name"
              placeholder="请输入竞赛名称（需与《厦门大学信息学院（特色化示范性软件学院）本科生学业竞赛项目库》中名称完全一致）"
              :maxlength="200"
              show-count
            />
            <div class="form-item-help">竞赛名称不能为空，长度不超过200字符</div>
          </a-form-item>
          
          <div class="form-row">
            <a-form-item label="竞赛级别" name="competition_level" style="flex: 1; margin-right: 16px;">
              <a-select v-model:value="formData.competition_level" placeholder="请选择竞赛级别">
                <a-select-option value="national">国家级</a-select-option>
                <a-select-option value="provincial">省级</a-select-option>
              </a-select>
              <div class="form-item-help">请选择竞赛级别</div>
            </a-form-item>
            
            <a-form-item label="竞赛类别" name="competition_category" style="flex: 1;">
              <a-select v-model:value="formData.competition_category" placeholder="请选择竞赛类别">
                <a-select-option value="a_plus">A+类</a-select-option>
                <a-select-option value="a">A类</a-select-option>
                <a-select-option value="a_minus">A-类</a-select-option>
              </a-select>
              <div class="form-item-help">请选择竞赛类别</div>
            </a-form-item>
          </div>
          

          
          <a-form-item label="获奖等级" name="award_level">
            <a-select v-model:value="formData.award_level" placeholder="请选择获奖等级">
              <a-select-option value="first_plus">一等奖及以上</a-select-option>
              <a-select-option value="second">二等奖</a-select-option>
              <a-select-option value="third">三等奖</a-select-option>
            </a-select>
            <div class="form-item-help">请选择获奖等级</div>
          </a-form-item>
          

          
          <a-form-item label="项目类型" name="project_type">
            <a-radio-group v-model:value="formData.project_type" button-style="solid">
              <a-radio-button value="individual">个人项目</a-radio-button>
              <a-radio-button value="group">团体项目</a-radio-button>
            </a-radio-group>
            <div class="form-item-help">请选择项目类型</div>
          </a-form-item>
          
          <!-- 个人项目 -->
          <template v-if="formData.project_type === 'individual'">
            <a-form-item label="个人独立完成" name="is_individual_project">
              <a-checkbox v-model:checked="formData.is_individual_project">确认勾选"个人独立完成"选项</a-checkbox>
              <div class="form-item-help">个人独立完成：项目仅由申请人一人完成</div>
            </a-form-item>
          </template>
          
          <!-- 团体项目 -->
          <template v-if="formData.project_type === 'group'">
            <div class="form-row">
              <a-form-item label="团队总人数" name="team_size" style="flex: 1; margin-right: 16px;">
                <a-input-number
                  v-model:value="formData.team_size"
                  :min="2"
                  :max="5"
                  :step="1"
                  placeholder="请输入团队总人数"
                />
                <div class="form-item-help">团队总人数范围：2-5人</div>
              </a-form-item>
              
              <a-form-item label="本人在团队中的角色" name="team_role" style="flex: 1;">
                <a-select v-model:value="formData.team_role" placeholder="请选择本人在团队中的角色">
                  <a-select-option value="captain">队长</a-select-option>
                  <a-select-option value="member_2_3">排序2-3的队员</a-select-option>
                  <a-select-option value="member_4_5">排序4-5的队员</a-select-option>
                  <a-select-option value="core_member">其他核心成员</a-select-option>
                </a-select>
                <div class="form-item-help">请选择您在团队中的角色</div>
              </a-form-item>
            </div>
            
            <a-form-item label="团队所有成员姓名及学号">
              <div class="team-members-container">
                <div v-for="(member, index) in formData.team_members" :key="index" class="team-member-item" v-if="index < formData.team_size">
                  <div class="team-member-header">
                    <span>成员{{ index + 1 }}:</span>
                  </div>
                  <div class="team-member-fields">
                    <a-input
                      v-model:value="member.name"
                      placeholder="姓名"
                      style="width: 150px; margin-right: 16px;"
                    />
                    <a-input
                      v-model:value="member.school_id"
                      placeholder="学号"
                      style="width: 150px;"
                    />
                  </div>
                </div>
              </div>
              <div class="form-item-help">按贡献顺序填写，最多填写5人</div>
            </a-form-item>
          </template>
          
          <!-- 关闭普通竞赛表单模板 -->
          </template>
          
          <!-- CCF CSP认证表单 -->
          <template v-else-if="formData.competition_type === 'csp'">
            <a-form-item label="全国排名等级" name="csp_rank_percentage">
              <a-radio-group v-model:value="formData.csp_rank_percentage">
                <a-radio-button value="0.2">排名前0.2% (等同全国一等奖)</a-radio-button>
                <a-radio-button value="1.5">排名前1.5% (等同全国二等奖)</a-radio-button>
                <a-radio-button value="3">排名前3% (等同全国三等奖)</a-radio-button>
              </a-radio-group>
              <div class="form-item-help">根据您的CCF CSP认证全国排名选择对应的等级</div>
            </a-form-item>
          </template>
        </template>
        
        <!-- 证明材料上传 -->
        <a-form-item label="证明材料">
          <a-upload
            v-model:file-list="fileList"
            :before-upload="beforeUpload"
            :custom-request="customUploadRequest"
            :auto-upload="false"
            :max-count="3"
            :multiple="true"
            accept=".jpg,.jpeg,.png"
          >
            <a-button icon="UploadOutlined">点击上传</a-button>
            <span style="margin-left: 8px;">支持JPG、PNG格式，单个文件不超过10MB</span>
          </a-upload>
          
          <!-- 文件预览列表 -->
          <div class="file-preview-list">
            <div 
              v-for="(file, index) in fileList" 
              :key="file.uid || index"
              class="file-preview-item"
            >
              <!-- 缩略图 -->
              <div class="file-thumbnail">
                <img 
                  :src="file.preview || file.url"
                  @click="openPreviewModal(file, index)"
                  alt="预览"
                />
              </div>
              
              <!-- 文件信息 -->
              <div class="file-info">
                <div class="file-name">{{ file.name }}</div>
                <div class="file-meta">
                  <span>{{ formatFileSize(file.size) }}</span>
                  <span>{{ file.type || getFileType(file.name) }}</span>
                </div>
              </div>
              
              <!-- 操作按钮 -->
              <div class="file-actions">
                <a-button 
                  type="text" 
                  size="small" 
                  @click="openPreviewModal(file, index)"
                >
                  预览
                </a-button>
                <a-button 
                  type="text" 
                  size="small" 
                  danger 
                  @click="removeFile(index)"
                >
                  删除
                </a-button>
              </div>
            </div>
          </div>
        </a-form-item>
        
        <!-- 预估加分显示 -->
        <div v-if="estimatedScore !== null" class="score-preview">
          <a-alert
            message="预估加分"
            :description="`根据您填写的信息，预估可获得加分：${estimatedScore}分`"
            type="info"
            show-icon
          />
        </div>
        
        <!-- 提交按钮 -->
        <div class="form-actions">
          <a-button @click="handleReset" :disabled="loading">重置</a-button>
          <a-button type="primary" html-type="submit" :loading="loading">
            {{ loading ? '提交中...' : '提交申请' }}
          </a-button>
        </div>
      </a-form>
    </a-card>
    
    <!-- 预览模态框 -->
    <a-modal
      v-model:open="previewModalVisible"
      :title="previewFileName"
      :width="previewModalWidth"
      :footer="null"
      @cancel="closePreviewModal"
    >
      <div class="preview-content">
        <!-- 图片预览 -->
        <div class="image-preview-container">
          <div 
            class="preview-image-wrapper"
            :style="{
              transform: `scale(${previewScale}) rotate(${previewRotation}deg)`
            }"
          >
            <img :src="previewImageSrc" alt="预览" />
          </div>
          
          <!-- 图片操作按钮 -->
          <div class="preview-actions">
            <a-button @click="rotateImage(-90)">向左旋转</a-button>
            <a-button @click="zoomOut">缩小</a-button>
            <a-button @click="resetPreview">重置</a-button>
            <a-button @click="zoomIn">放大</a-button>
            <a-button @click="rotateImage(90)">向右旋转</a-button>
          </div>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { UploadOutlined } from '@ant-design/icons-vue'
import { message, Modal } from 'ant-design-vue'
import api from '../../utils/api'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const fileList = ref([])

// 预览相关状态
const previewModalVisible = ref(false)
const previewFile = ref(null)
const previewFileIndex = ref(null)
const previewImageSrc = ref('')
const previewFileName = ref('')
const previewScale = ref(1)
const previewRotation = ref(0)
const previewModalWidth = ref(800)

// 保存所有创建的ObjectURL，用于清理
const objectUrls = ref([])

// 折叠面板状态
const icpcCollapseActiveKey = ref(['icpc_ccpc'])
const cspCollapseActiveKey = ref(['ccf_csp'])

// 处理编辑功能：从URL中获取申请数据
const route = useRoute()
const routeQuery = ref(route.query)

// 编辑模式：检查是否是编辑状态
const isEditMode = computed(() => {
  return route.query.isEdit === 'true'
})

// 应用ID，用于编辑操作
const applicationId = ref('')

// 现有预估分数，用于编辑模式下的表单提交
const existingEstimatedScore = ref(0)

// 申请详情数据，用于编辑模式下的表单提交
const applicationData = ref({})

// 编辑模式下，从后端获取申请详情并填充表单
onMounted(async () => {
  if (isEditMode.value) {
    try {
      loading.value = true
      console.log('编辑模式：从API获取申请详情')
      
      // 从URL中获取申请ID
      let id = route.query.id || ''
      
      if (!id) {
        // 如果URL中没有id，尝试从URL路径中获取
        const pathSegments = route.path.split('/')
        id = pathSegments[pathSegments.length - 1]
      }
      
      if (!id) {
        throw new Error('缺少申请ID')
      }
      
      // 调用API获取完整的申请详情
      const applicationDetailResponse = await api.getApplicationDetail(id)
      console.log('获取到的申请详情响应：', applicationDetailResponse)
      
      // 处理嵌套的申请详情结构
      const applicationDetail = applicationDetailResponse.data || applicationDetailResponse
      applicationData.value = applicationDetail.application_data || applicationDetail
      const applicationType = applicationDetail.application_type || applicationData.value.type || ''
      
      console.log('处理后的申请数据：', {
        applicationType,
        applicationData: applicationData.value,
        attachments: applicationDetail.attachments || []
      })
      
      // 保存申请ID用于后续编辑操作
      applicationId.value = id
      
      // 初始化现有预估分数，用于表单提交
      existingEstimatedScore.value = applicationData.estimated_score || 0
      
      // 创建application_type到projectCategory和projectType的映射表
      const typeMapping = {
        'english_scores': {
          category: 'english_cet',
          type: 'english_cet'
        },
        'academic_papers': {
          category: 'academic_excellence',
          type: 'research_achievements',
          subType: 'academic_paper'
        },
        'patent_works': {
          category: 'academic_excellence',
          type: 'research_achievements',
          subType: 'invention_patent'
        },
        'academic_competitions': {
          category: 'academic_excellence',
          type: 'academic_competition'
        },
        'innovation_projects': {
          category: 'academic_excellence',
          type: 'innovation_project'
        },
        'ccf_csp_certifications': {
          category: 'academic_excellence',
          type: 'academic_competition'
        },
        'international_internships': {
          category: 'comprehensive_performance',
          type: 'international_internship'
        },
        'military_services': {
          category: 'comprehensive_performance',
          type: 'military_service'
        },
        'volunteer_services': {
          category: 'comprehensive_performance',
          type: 'volunteer_service'
        },
        'honorary_titles': {
          category: 'comprehensive_performance',
          type: 'honorary_title'
        },
        'social_works': {
          category: 'comprehensive_performance',
          type: 'social_work'
        },
        'sports_competitions': {
          category: 'comprehensive_performance',
          type: 'sports_competition'
        }
      }
      
      // 获取映射信息
      const mapping = typeMapping[applicationType] || {}
      
      // 填充表单数据
      // 首先设置项目大类和类型
      formData.projectCategory = mapping.category || ''
      formData.projectType = mapping.type || ''
      if (mapping.subType) {
        formData.subProjectType = mapping.subType
      }
      
      // 根据不同的application_type填充具体字段
      if (applicationType === 'english_scores') {
        // 英语四六级
        formData.projectType = applicationData.exam_type === 'cet4' ? 'english_cet4' : 'english_cet6'
        formData.exam_score = applicationData.exam_score
      } else if (applicationType === 'academic_papers') {
        // 学术论文
        formData.paper_title = applicationData.paper_title || ''
        formData.journal_category = applicationData.journal_category || ''
        formData.is_independent_author = applicationData.is_independent_author ? 'true' : 'false'
        formData.is_co_first_author = applicationData.is_co_first_author ? 'true' : 'false'
        formData.author_rank = applicationData.author_rank || ''
        formData.is_xmu_first_unit = applicationData.is_xmu_first_unit ? 'true' : 'false'
      } else if (applicationType === 'patent_works') {
        // 发明专利
        formData.patent_title = applicationData.paper_title || ''
        formData.author_type = applicationData.author_type || ''
        formData.is_xmu_first_unit = applicationData.is_xmu_first_unit ? 'true' : 'false'
      } else if (applicationType === 'academic_competitions') {
        // 学术竞赛
        formData.competition_name = applicationData.competition_specific_name || applicationData.competition_name || ''
        formData.competition_level = applicationData.competition_level || ''
        formData.award_level = applicationData.award_level || ''
        formData.project_type = applicationData.project_type || ''
        formData.team_size = applicationData.team_size || 1
        formData.team_role = applicationData.team_role || ''
      } else if (applicationType === 'innovation_projects') {
        // 创新项目
        formData.project_name = applicationData.project_name || ''
        formData.project_level = applicationData.project_level || ''
        formData.is_responsible_person = applicationData.is_responsible_person ? 'true' : 'false'
      } else if (applicationType === 'ccf_csp_certifications') {
        // CCF CSP认证
        formData.competition_type = 'csp'
        formData.csp_rank_percentage = applicationData.csp_rank_percentage || ''
      } else if (applicationType === 'international_internships') {
        // 国际组织实习
        formData.institution_name = applicationData.organization_name || ''
        formData.internship_duration_type = applicationData.internship_duration_type || ''
      } else if (applicationType === 'military_services') {
        // 参军入伍
        formData.military_service_duration = applicationData.military_service_duration || ''
      } else if (applicationType === 'volunteer_services') {
        // 志愿服务
        formData.volunteer_service_type = applicationData.volunteer_service_type || ''
        formData.service_hours = applicationData.service_hours || 0
        formData.recognition_name = applicationData.activity_name || ''
      } else if (applicationType === 'honorary_titles') {
        // 荣誉称号
        formData.honor_name = applicationData.title_name || ''
        formData.honor_level = applicationData.honor_level || ''
        formData.awarding_year = applicationData.awarding_year || ''
        formData.is_collective = applicationData.is_collective ? 'true' : 'false'
      } else if (applicationType === 'social_works') {
        // 社会工作
        formData.position_name = applicationData.organization || ''
        formData.term_years = applicationData.work_period || ''
        formData.teacher_score = applicationData.teacher_score || ''
      } else if (applicationType === 'sports_competitions') {
        // 体育竞赛
        formData.competition_name = applicationData.competition_name || ''
        formData.competition_level = applicationData.competition_level || ''
        formData.award_level = applicationData.achievement || ''
        formData.is_team_project = applicationData.is_team_project ? 'true' : 'false'
        formData.team_size = applicationData.team_size || 1
        formData.project_type = applicationData.project_type || ''
      }
      
      // 填充其他表单字段
      // 根据项目类型填充不同的字段
      if (formData.projectType === 'english_cet4' || formData.projectType === 'english_cet6') {
        // 英语四六级
        formData.exam_score = applicationData.exam_score
      } else if (formData.projectType === 'academic_competition') {
        // 学术竞赛
        formData.competition_name = applicationData.competition_name || ''
        formData.competition_level = applicationData.competition_level || ''
        formData.award_level = applicationData.award_level || ''
        formData.project_type = applicationData.project_type || ''
        formData.team_size = applicationData.team_size || 1
        formData.team_role = applicationData.team_role || ''
      } else if (formData.subProjectType === 'invention_patent') {
        // 发明专利
        formData.patent_title = applicationData.paper_title || ''
        formData.author_type = applicationData.author_type || ''
        formData.is_xmu_first_unit = applicationData.is_xmu_first_unit || 'true'
      } else if (formData.projectType === 'innovation_project') {
        // 创新项目
        formData.project_name = applicationData.project_name || ''
        formData.project_level = applicationData.project_level || ''
        formData.is_responsible_person = applicationData.is_responsible_person || 'false'
      } else if (formData.projectType === 'volunteer_service') {
        // 志愿服务
        formData.volunteer_service_type = applicationData.volunteer_service_type || ''
        formData.service_hours = applicationData.service_hours || 0
        formData.recognition_name = applicationData.recognition_name || ''
      } else if (formData.projectType === 'honorary_title') {
        // 荣誉称号
        formData.honor_name = applicationData.honor_name || ''
        formData.honor_level = applicationData.honor_level || ''
        formData.awarding_year = applicationData.awarding_year || ''
        formData.is_collective = applicationData.is_collective || 'false'
      } else if (formData.projectType === 'social_work') {
        // 社会工作
        formData.position_name = applicationData.position || ''
        formData.term_years = applicationData.work_period || ''
        formData.teacher_score = applicationData.teacher_score || ''
      } else if (formData.projectType === 'sports_competition') {
        // 体育竞赛
        formData.competition_name = applicationData.competition_name || ''
        formData.competition_level = applicationData.competition_level || ''
        formData.award_level = applicationData.achievement || ''
        formData.is_team_project = applicationData.is_team_project ? 'true' : 'false'
        formData.team_size = applicationData.team_size || 1
        formData.project_type = applicationData.project_type || ''
      }
      
      // 处理附件
      // 使用URL查询参数中的附件数据
      const attachments = []
      
      // 检查所有可能的附件字段
      const attachmentFields = ['attachments', 'screenshot', 'score_report', 'file_url', 'path', 'files', 'paper_attachments', 'academic_paper_attachments', 'document_urls', 'file_urls', 'file_paths', 'attachment_urls', 'proof_materials', 'materials', 'documents']
      
      for (const field of attachmentFields) {
        if (applicationDetail[field]) {
          if (Array.isArray(applicationDetail[field])) {
            attachments.push(...applicationDetail[field])
          } else {
            attachments.push(applicationDetail[field])
          }
        }
      }
      
      // 处理附件，转换为Upload组件需要的格式
      if (attachments.length > 0) {
        const processedFiles = []
        const urlSet = new Set() // 用于去重
        
        for (const attachment of attachments) {
          // 创建符合Upload组件要求的文件对象
          // 注意：这里只是模拟文件对象，实际编辑时可能需要重新上传文件
          // 或者从URL创建Blob对象
          let fileObj = {}
          let fileUrl = ''
          
          if (typeof attachment === 'string') {
            // 如果是字符串URL
            fileUrl = attachment
          } else if (typeof attachment === 'object' && attachment !== null) {
            // 如果是对象
            fileUrl = attachment.url || attachment.file_url || attachment.path || ''
          }
          
          // 去重：如果URL已经处理过，跳过
          if (!fileUrl || urlSet.has(fileUrl)) {
            continue
          }
          
          urlSet.add(fileUrl)
          
          // 从URL中提取文件名
          const fileName = fileUrl.split('/').pop() || `附件${processedFiles.length + 1}`
          fileObj = {
            uid: `${Date.now()}-${Math.random()}`,
            name: fileName,
            status: 'done',
            url: fileUrl,
            type: fileUrl.endsWith('.pdf') ? 'application/pdf' : 'image/jpeg',
            existing: true // 标记为已存在的文件，用于后续提交处理
          }
          
          processedFiles.push(fileObj)
        }
        
        fileList.value = processedFiles
      }
      
      console.log('表单数据填充完成')
      message.success('编辑数据加载成功')
    } catch (error) {
      console.error('获取申请详情失败:', error)
      message.error('获取申请详情失败，请稍后重试')
    } finally {
      loading.value = false
    }
  }
})

// 表单数据
const formData = reactive({
  projectCategory: '',
  projectType: '',
  subProjectType: '', // 新增：科研成果子类型（学术论文/发明专利）
  // 学术论文专用字段
  paper_title: '',
  journal_category: '',
  is_independent_author: 'false',
  is_co_first_author: 'false',
  author_rank: '',
  is_xmu_first_unit: 'true',
  // 发明专利专用字段
  patent_title: '',
  author_type: '', // 新增：作者类型
  // 学术竞赛专用字段
  competition_type: '', // 竞赛类型（竞赛/CCF CSP认证）
  
  // 普通竞赛字段
  competition_name: '', // 竞赛名称
  competition_level: '', // 竞赛级别
  competition_category: '', // 竞赛类别
  competition_organizer: '', // 竞赛主办单位
  competition_date: '', // 竞赛举办时间
  award_date: '', // 获奖时间
  award_level: '', // 获奖等级
  certificate_number: '', // 获奖证书编号
  project_type: '', // 项目类型（个人/团体）
  // 团体项目字段
  team_size: 1, // 团队总人数
  team_role: '', // 本人在团队中的角色
  team_members: [{ name: '', school_id: '' }, { name: '', school_id: '' }, { name: '', school_id: '' }, { name: '', school_id: '' }, { name: '', school_id: '' }], // 团队成员
  // 个人项目字段
  is_individual_project: false, // 个人独立完成
  // 作品相关信息（已移除）
  // work_name: '', // 作品名称
  // work_description: '', // 作品简介
  // is_iteration: 'false', // 是否为迭代升级作品
  // original_work_name: '', // 原作品名称
  // iteration_description: '', // 迭代升级说明
  // work_filing_status: '', // 作品备案情况
  // filing_number: '', // 备案编号
  // filing_date: '', // 备案时间
  
  // ICPC/CCPC竞赛字段（已移除）
  // icpc_specific_name: '', // ICPC/CCPC竞赛具体名称
  // icpc_site: '', // 竞赛站点/场次信息
  
  // CCF CSP认证字段
  csp_rank_percentage: '', // CCF CSP全国排名百分比
  // 创新项目字段
  project_name: '', // 项目名称
  project_level: '', // 项目级别
  // 根据用户要求，不需要填写项目周期，移除该字段
  // project_duration: '', // 项目周期
  is_responsible_person: 'false', // 是否为负责人
  // 国际组织实习字段
  internship_duration_type: '', // 实习时长类型（满一学年/满一学期）
  institution_name: '', // 实习机构名称
  country: '', // 国家
  // 参军入伍字段
  military_service_duration: '', // 服兵役时长类型（1-2年/2年以上）
  military_unit: '', // 服役部队
  // 志愿服务字段
  volunteer_service_type: '', // 志愿服务类型（service_hours/recognition）
  service_name: '', // 服务名称
  service_hours: 0, // 服务时长
  service_date: null, // 服务时间
  is_special_volunteer: 'false', // 是否为特殊志愿者（大型赛会/支教）
  // 志愿表彰字段
  recognition_name: '', // 表彰名称
  recognition_level: '', // 表彰级别
  recognition_type: '', // 表彰类型（团队/个人）
  recognition_date: null, // 表彰时间
  // 移除不需要的字段
  // patent_number: '',
  // patent_type: '',
  // patent_status: ''
})

// 表单验证规则
const formRules = reactive({
  projectCategory: [{ required: true, message: '请选择申请大类', trigger: 'change' }],
  projectType: [{ required: true, message: '请选择申请类型', trigger: 'change' }],
  subProjectType: [{ required: formData.projectType === 'research_achievements', message: '请选择科研成果类型', trigger: 'change' }],
  // 已移除冗余字段的验证规则
  // title: [{ required: true, message: '请输入申请标题', trigger: 'blur' }],
  // description: [{ required: true, message: '请输入申请描述', trigger: 'blur' }],
  // user_explanation: [{ required: false }],
  // 学术论文验证规则
  paper_title: [{ 
    required: formData.projectType === 'research_achievements' && formData.subProjectType === 'academic_paper', 
    message: '请输入论文标题', 
    trigger: 'blur' 
  }, { 
    max: 200, 
    message: '论文标题长度不超过200字符', 
    trigger: 'blur' 
  }],
  // 移除论文DOI验证规则
  // paper_doi: [{ 
  //   required: formData.projectType === 'academic_paper', 
  //   message: '请输入论文DOI', 
  //   trigger: 'blur' 
  // }],
  journal_category: [{ 
    required: formData.projectType === 'research_achievements' && formData.subProjectType === 'academic_paper', 
    message: '请选择期刊/会议分类', 
    trigger: 'change' 
  }],
  is_independent_author: [{ 
    required: formData.projectType === 'research_achievements' && formData.subProjectType === 'academic_paper', 
    message: '请选择是否为独立作者', 
    trigger: 'change' 
  }],
  is_co_first_author: [{ 
    required: formData.projectType === 'research_achievements' && formData.subProjectType === 'academic_paper' && formData.is_independent_author === 'false', 
    message: '请选择是否为共同第一作者', 
    trigger: 'change' 
  }],
  author_rank: [{ 
    required: formData.projectType === 'research_achievements' && formData.subProjectType === 'academic_paper' && formData.is_independent_author === 'false' && formData.is_co_first_author === 'false', 
    message: '请选择作者排序', 
    trigger: 'change' 
  }],
  is_xmu_first_unit: [{ 
    required: formData.projectType === 'research_achievements' && (formData.subProjectType === 'academic_paper' || formData.subProjectType === 'invention_patent'), 
    message: '请选择厦门大学是否为第一单位', 
    trigger: 'change' 
  }, { 
    validator: (rule, value) => {
      if ((formData.projectType === 'research_achievements' && (formData.subProjectType === 'academic_paper' || formData.subProjectType === 'invention_patent')) && value === 'false') {
        return Promise.reject(new Error('厦门大学必须为第一单位'))
      } else {
        return Promise.resolve()
      }
    },
    trigger: 'change'
  }],
  // 学术竞赛验证规则
  competition_type: [{ required: formData.projectType === 'academic_competition', message: '请选择竞赛类型', trigger: 'change' }],
  
  // 普通竞赛验证规则
  competition_name: [{ required: formData.projectType === 'academic_competition' && formData.competition_type === 'competition', message: '请输入竞赛名称', trigger: 'blur' }],
  competition_level: [{ required: formData.projectType === 'academic_competition' && formData.competition_type === 'competition', message: '请选择竞赛级别', trigger: 'change' }],
  competition_category: [{ required: formData.projectType === 'academic_competition' && formData.competition_type === 'competition', message: '请选择竞赛类别', trigger: 'change' }],
  award_level: [{ required: formData.projectType === 'academic_competition' && formData.competition_type === 'competition', message: '请选择获奖等级', trigger: 'change' }],
  project_type: [{ required: formData.projectType === 'academic_competition' && formData.competition_type === 'competition', message: '请选择项目类型', trigger: 'change' }],
  
  // 团体项目验证规则
  team_size: [{ required: formData.projectType === 'academic_competition' && formData.competition_type === 'competition' && formData.project_type === 'group', message: '请输入团队总人数', trigger: 'blur' },
             { type: 'number', min: 2, message: '团队人数至少为2人', trigger: 'blur' }],
  team_role: [{ required: formData.projectType === 'academic_competition' && formData.competition_type === 'competition' && formData.project_type === 'group', message: '请选择本人在团队中的角色', trigger: 'change' }],
  
  // 个人项目验证规则
  is_individual_project: [{ required: formData.projectType === 'academic_competition' && formData.competition_type === 'competition' && formData.project_type === 'individual', message: '请确认个人独立完成', trigger: 'change' }],
  
  // CCF CSP认证验证规则
  csp_rank_percentage: [{ required: formData.projectType === 'academic_competition' && formData.competition_type === 'csp', message: '请输入全国排名百分比', trigger: 'blur' }],
  
  // 作品相关验证规则（已移除）
  // work_description: [{ max: 500, message: '作品简介限500字以内', trigger: 'blur' }],
  // iteration_description: [{ max: 300, message: '迭代升级说明限300字以内', trigger: 'blur' }],
  // 创新项目验证规则
  project_name: [{ required: formData.projectType === 'innovation_project', message: '请输入项目名称', trigger: 'blur' }],
  project_level: [{ required: formData.projectType === 'innovation_project', message: '请选择项目级别', trigger: 'change' }],
  project_status: [{ required: formData.projectType === 'innovation_project', message: '请选择项目状态', trigger: 'change' }],
  // CCF CSP验证规则
  exam_score: [{ required: formData.projectType === 'ccf_csp', message: '请输入考试成绩', trigger: 'blur' }],
  exam_date: [{ required: formData.projectType === 'ccf_csp', message: '请选择考试日期', trigger: 'change' }],
  // 英语四六级验证规则
  exam_score: [{ required: formData.projectType === 'english_cet4' || formData.projectType === 'english_cet6', message: '请输入考试成绩', trigger: 'blur' }],
  // 志愿服务验证规则
  volunteer_service_type: [{ required: formData.projectType === 'volunteer_service', message: '请选择服务类型', trigger: 'change' }],
  // 志愿服务（时长）验证规则
  service_hours: [{ required: formData.projectType === 'volunteer_service' && formData.volunteer_service_type === 'service_hours', message: '请输入服务时长', trigger: 'blur' }],
  // 志愿表彰验证规则
  recognition_name: [{ required: formData.projectType === 'volunteer_service' && formData.volunteer_service_type === 'recognition', message: '请输入表彰名称', trigger: 'blur' }],
  recognition_level: [{ required: formData.projectType === 'volunteer_service' && formData.volunteer_service_type === 'recognition', message: '请选择表彰级别', trigger: 'change' }],
  recognition_type: [{ required: formData.projectType === 'volunteer_service' && formData.volunteer_service_type === 'recognition', message: '请选择表彰类型', trigger: 'change' }],
  team_role: [{ required: formData.projectType === 'volunteer_service' && formData.volunteer_service_type === 'recognition' && formData.recognition_type === 'team', message: '请选择团队角色', trigger: 'change' }],
  // 社会工作验证规则
  position_name: [{ required: formData.projectType === 'social_work', message: '请输入职务名称', trigger: 'blur' }],
  term_years: [{ required: formData.projectType === 'social_work', message: '请选择任期年数', trigger: 'change' }],
  teacher_score: [{ required: formData.projectType === 'social_work', message: '请输入老师打分', trigger: 'blur' }],
  // 荣誉称号验证规则
  honor_name: [{ required: formData.projectType === 'honorary_title', message: '请输入荣誉名称', trigger: 'blur' }],
  honor_level: [{ required: formData.projectType === 'honorary_title', message: '请选择荣誉级别', trigger: 'change' }],
  awarding_year: [{ required: formData.projectType === 'honorary_title', message: '请输入授予学年', trigger: 'blur' }],
  is_collective: [{ required: formData.projectType === 'honorary_title', message: '请选择是否是集体荣誉', trigger: 'change' }],
  // 发明专利验证规则
  patent_title: [{ required: formData.subProjectType === 'invention_patent', message: '请输入专利名称', trigger: 'blur' }],
  // CCF CSP认证验证规则（学术竞赛下）
  csp_rank_percentage: [{ required: formData.projectType === 'academic_competition' && formData.competition_type === 'csp', message: '请选择全国排名等级', trigger: 'change' }],
  // 国际组织实习验证规则
  institution_name: [{ required: formData.projectType === 'international_internship', message: '请输入实习机构名称', trigger: 'blur' }],
  internship_duration_type: [{ required: formData.projectType === 'international_internship', message: '请选择实习时长类型', trigger: 'change' }],
  // 参军入伍验证规则
  military_service_duration: [{ required: formData.projectType === 'military_service', message: '请选择服兵役时长类型', trigger: 'change' }],
  // 创新项目验证规则
  project_name: [{ required: formData.projectType === 'innovation_project', message: '请输入项目名称', trigger: 'blur' }],
  project_level: [{ required: formData.projectType === 'innovation_project', message: '请选择项目级别', trigger: 'change' }]
})

// 预估加分计算
const estimatedScore = computed(() => {
  if (!formData.projectType) return 0
  
  // 计算原始分数
  let score = 0
  
  // 检查是否为科研成果下的学术论文
  const isAcademicPaper = formData.projectType === 'academic_paper' || formData.subProjectType === 'academic_paper'
  // 检查是否为科研成果下的发明专利
  const isInventionPatent = formData.subProjectType === 'invention_patent'
  
  // 获取实际的项目类型，优先使用formData.projectType，如果为空则使用applicationType
  let projectType = formData.projectType || applicationType
  
  // 处理科研成果子类型
  if (projectType === 'research_achievements') {
    if (formData.subProjectType === 'academic_paper') {
      projectType = 'academic_paper'
    } else if (formData.subProjectType === 'invention_patent') {
      projectType = 'invention_patent'
    }
  }
  
  switch (projectType) {
    case 'academic_paper':
      // 学术论文加分规则不变
      // 基础分值
      let baseScore = 0
      switch (formData.journal_category) {
        case 'nature_science_cell':
        case 'nature_science_cell_sub':
          baseScore = 20 // 特殊期刊加分：20分
          break
        case 'a_class':
        case 'ict_recommended':
          baseScore = 10 // A类：10分
          break
        case 'b_class':
        case 'high_level_chinese':
          baseScore = 6 // B类：6分
          break
        case 'c_class':
          baseScore = 1 // C类：1分
          break
        default:
          baseScore = 0
      }
      
      // 作者排序比例
      let authorRatio = 0
      if (formData.is_independent_author === 'true') {
        authorRatio = 1.0
      } else {
        if (formData.is_co_first_author === 'true') {
          authorRatio = 0.5
        } else {
          if (formData.author_rank === '1') {
            authorRatio = 0.8
          } else if (formData.author_rank === '2') {
            authorRatio = 0.2
          }
        }
      }
      
      score = baseScore * authorRatio
      break
      
    case 'invention_patent':
      // 发明专利新加分规则
      // 基础分值：2分
      const basePatentScore = 2
      
      // 作者类型加分比例
      let authorTypeRatio = 0
      if (formData.author_type === 'first_author_except_teacher') {
        authorTypeRatio = 0.8 // 除老师外第一作者：80%
      } else if (formData.author_type === 'independent_author') {
        authorTypeRatio = 1.0 // 独立作者：100%
      }
      
      // 计算最终得分
      score = basePatentScore * authorTypeRatio
      break
      
    case 'academic_competition':
      // 学术竞赛加分规则
      let baseCompetitionScore = 0
      
      // 竞赛类别基础分值
      const categoryScoreMap = {
        'a_plus': 15, // A+类
        'a': 10,      // A类
        'a_minus': 5   // A-类
      }
      
      // 获奖等级加分比例
      const awardRatioMap = {
        'first_plus': 1.0,  // 一等奖及以上
        'second': 0.6,       // 二等奖
        'third': 0.3         // 三等奖
      }
      
      // 竞赛级别加分倍数
      const levelMultiplierMap = {
        'national': 1.0,     // 国家级
        'provincial': 0.6    // 省级
      }
      
      // 团队角色加分比例
      const teamRoleRatioMap = {
        'captain': 1.0,          // 队长
        'member_2_3': 0.7,       // 排序2-3的队员
        'member_4_5': 0.4,       // 排序4-5的队员
        'core_member': 0.5       // 其他核心成员
      }
      
      // 特殊处理CCF CSP认证
      if (formData.competition_type === 'csp') {
        // CCF CSP认证按照A-类竞赛标准加分，直接使用固定分值
        if (formData.csp_rank_percentage === '0.2') {
          // 排名前0.2%，等同全国一等奖
          score = 10
        } else if (formData.csp_rank_percentage === '1.5') {
          // 排名前1.5%，等同全国二等奖
          score = 5
        } else if (formData.csp_rank_percentage === '3') {
          // 排名前3%，等同全国三等奖
          score = 2
        } else {
          score = 0
        }
      } else {
        // 普通竞赛计算逻辑
        // 计算基础分值
        baseCompetitionScore = categoryScoreMap[formData.competition_category] || 0
        
        // 应用获奖等级比例
        const awardRatio = awardRatioMap[formData.award_level] || 0
        
        // 应用竞赛级别倍数
        const levelMultiplier = levelMultiplierMap[formData.competition_level] || 1.0
        
        // 计算个人贡献比例
        let personalContributionRatio = 1.0
        if (formData.project_type === 'group') {
          personalContributionRatio = teamRoleRatioMap[formData.team_role] || 0.5
        }
        
        // 计算最终得分
        score = baseCompetitionScore * awardRatio * levelMultiplier * personalContributionRatio
      }
      break
      
    case 'sports_competition':
      // 体育竞赛加分规则
      let baseSportsScore = 0
      
      // 体育竞赛加分细则：根据竞赛级别和获奖等级确定基础分值
      if (formData.competition_level === 'international') {
        // 国际级竞赛
        if (formData.award_level === 'champion') {
          baseSportsScore = 8.0
        } else if (formData.award_level === 'runner_up') {
          baseSportsScore = 6.5
        } else if (formData.award_level === 'third_place') {
          baseSportsScore = 5.0
        } else if (formData.award_level === 'fourth_to_eighth') {
          baseSportsScore = 3.5
        }
      } else if (formData.competition_level === 'national') {
        // 国家级竞赛
        if (formData.award_level === 'champion') {
          baseSportsScore = 5.0
        } else if (formData.award_level === 'runner_up') {
          baseSportsScore = 3.5
        } else if (formData.award_level === 'third_place') {
          baseSportsScore = 2.0
        } else if (formData.award_level === 'fourth_to_eighth') {
          baseSportsScore = 1.0
        }
      }
      
      // 根据项目类型调整得分
      if (formData.is_team_project === 'true') {
        // 团队项目：按参赛人数平均计算加分值
        if (formData.team_size && formData.team_size > 0) {
          score = baseSportsScore / formData.team_size
        } else {
          score = baseSportsScore
        }
      } else {
        // 个人或二人项目：加分按同一级别团体项目获奖加分值的1/3计算
        score = baseSportsScore / 3
      }
      break
      
    case 'volunteer_service':
      if (formData.volunteer_service_type === 'service_hours') {
        // 志愿服务（时长）加分规则
        if (!formData.service_hours || formData.service_hours < 200) {
          score = 0
        } else {
          // 计算实际有效工时：大型赛会志愿者与支教活动工时减半
          let effectiveHours = formData.service_hours
          if (formData.is_special_volunteer === 'true') {
            effectiveHours = formData.service_hours / 2
          }
          
          // 超过200小时的部分，每2小时增加0.05分
          const excessHours = effectiveHours - 200
          const additionalScore = (excessHours / 2) * 0.05
          
          // 计算最终分数，最高1分
          score = Math.min(additionalScore, 1.0)
        }
      } else if (formData.volunteer_service_type === 'recognition') {
        // 志愿表彰加分规则
        const recognitionScoreMap = {
          // 个人表彰
          'individual': {
            'national': 1.0,
            'provincial': 0.5,
            'school': 0.25
          },
          // 团队队长
          'team_captain': {
            'national': 1.0,
            'provincial': 0.5,
            'school': 0.25
          },
          // 团队队员
          'team_member': {
            'national': 0.5,
            'provincial': 0.25,
            'school': 0.1
          }
        }
        
        let scoreKey = ''
        if (formData.recognition_type === 'individual') {
          scoreKey = 'individual'
        } else {
          scoreKey = formData.team_role === 'captain' ? 'team_captain' : 'team_member'
        }
        
        score = recognitionScoreMap[scoreKey]?.[formData.recognition_level] || 0
      }
      break
      
    case 'ccf_csp':
      if (formData.competition_type === 'csp') {
        // CCF CSP认证按照A-类竞赛标准加分，直接使用固定分值
        if (formData.csp_rank_percentage === '0.2') {
          // 排名前0.2%，等同全国一等奖
          score = 10
        } else if (formData.csp_rank_percentage === '1.5') {
          // 排名前1.5%，等同全国二等奖
          score = 5
        } else if (formData.csp_rank_percentage === '3') {
          // 排名前3%，等同全国三等奖
          score = 2
        } else {
          score = 0
        }
      } else {
        if (!formData.exam_score) score = 0
        else if (formData.exam_score >= 450) score = 5
        else if (formData.exam_score >= 350) score = 4
        else if (formData.exam_score >= 300) score = 3
        else if (formData.exam_score >= 200) score = 2
        else if (formData.exam_score >= 100) score = 1
        else score = 0
      }
      break
      
    case 'innovation_project':
      // 创新项目加分规则
      if (!formData.project_level || !formData.is_responsible_person) {
        score = 0
      } else {
        // 根据项目级别和是否为负责人计算分数
        const isLeader = formData.is_responsible_person === 'true'
        switch (formData.project_level) {
          case 'national':
            score = isLeader ? 1.0 : 0.3
            break
          case 'provincial':
            score = isLeader ? 0.5 : 0.2
            break
          case 'school':
            score = isLeader ? 0.1 : 0.05
            break
          default:
            score = 0
        }
        // 该项最多加2分
        score = Math.min(score, 2.0)
      }
      break
      
    case 'international_internship':
      // 国际组织实习加分规则
      if (!formData.internship_duration_type) {
        score = 0
      } else {
        switch (formData.internship_duration_type) {
          case 'full_year':
            score = 1.0
            break
          case 'half_year':
            score = 0.5
            break
          default:
            score = 0
        }
        // 该项最多加1分
        score = Math.min(score, 1.0)
      }
      break
      
    case 'military_service':
      // 参军入伍加分规则
      if (!formData.military_service_duration) {
        score = 0
      } else {
        switch (formData.military_service_duration) {
          case 'one_to_two_years':
            score = 1.0
            break
          case 'two_years_plus':
            score = 2.0
            break
          default:
            score = 0
        }
        // 该项最多加2分
        score = Math.min(score, 2.0)
      }
      break
      
    case 'honorary_title':
      // 荣誉称号加分规则
      if (!formData.honor_level) {
        score = 0
      } else {
        const honorScoreMap = {
          'national': 2.0,
          'provincial': 1.0,
          'school': 0.2
        }
        let baseScore = honorScoreMap[formData.honor_level] || 0
        
        // 集体荣誉得分减半
        if (formData.is_collective === 'true') {
          baseScore = baseScore / 2
        }
        
        // 计算最终分数，最高2分
        score = Math.min(baseScore, 2.0)
      }
      break
      
    case 'social_work':
      // 社会工作加分规则
      if (!formData.term_years || !formData.teacher_score) {
        score = 0
      } else {
        // 根据职务名称确定系数
        let coefficient = 1.0 // 默认系数
        const positionName = formData.position_name.toLowerCase()
        
        // 根据职务名称确定系数
        if (positionName.includes('执行主席') || positionName.includes('团总支书记')) {
          coefficient = 2.0
        } else if (positionName.includes('主席团') || positionName.includes('团总支副书记')) {
          coefficient = 1.5
        } else if (positionName.includes('部长') || positionName.includes('党支部书记') || positionName.includes('班长') || positionName.includes('团支部书记')) {
          coefficient = 1.0
        } else if (positionName.includes('副部长') || positionName.includes('社团社长') || positionName.includes('系团总支书记')) {
          coefficient = 0.75
        } else if (positionName.includes('委员') || positionName.includes('班委') || positionName.includes('志愿者') || positionName.includes('副社长') || positionName.includes('队长')) {
          coefficient = 0.5
        }
        
        // 计算基础得分
        const baseScore = (coefficient * formData.teacher_score) / 100
        
        // 根据任期年数调整得分
        let termAdjustedScore = baseScore
        if (formData.term_years === '0.5') {
          // 超过一学期但不满一年，减半计算
          termAdjustedScore = baseScore * 0.5
        } else {
          // 满一学年或以上，按实际年数计算
          termAdjustedScore = baseScore * parseFloat(formData.term_years)
        }
        
        // 计算最终分数，最高2分
        score = Math.min(termAdjustedScore, 2.0)
      }
      break
      
    default:
      // 默认情况，返回0表示无法计算预估分数
      score = 0
      break
  }
  
  // 应用大类加分上限
  if (formData.projectCategory === 'academic_excellence') {
    return parseFloat(Math.min(score, 15).toFixed(4)) // 学术专长成绩上限15分，保留4位小数
  } else if (formData.projectCategory === 'comprehensive_performance') {
    return parseFloat(Math.min(score, 5).toFixed(4)) // 综合表现加分上限5分，保留4位小数
  }
  
  return parseFloat(score.toFixed(4))
})

// 监听科研成果子类型变化，清空相关字段
const handleSubProjectTypeChange = () => {
  // 重置除了基本信息外的所有字段
  const basicFields = ['projectCategory', 'projectType', 'subProjectType']
  for (const field in formData) {
    if (!basicFields.includes(field)) {
      formData[field] = ''
    }
  }
  fileList.value = []
}

// 监听项目类型变化，清空表单并重新验证
const handleProjectTypeChange = () => {
  // 重置除了基本信息外的所有字段
  const basicFields = ['projectCategory', 'projectType'] // 已移除冗余字段
  for (const field in formData) {
    if (!basicFields.includes(field)) {
      formData[field] = ''
    }
  }
  fileList.value = []
  
  // 重新验证表单，确保文件上传验证被触发
  if (formRef.value) {
    formRef.value.validate()
  }
}

// 监听大类变化，清空项目类型
const handleCategoryChange = () => {
  formData.projectType = ''
  formData.subProjectType = ''
  handleProjectTypeChange() // 调用项目类型变化处理函数，清空相关字段
}





// 文件上传前校验（恢复为同步函数，Ant Design Vue的beforeUpload不支持异步）
const beforeUpload = (file) => {
  // 只允许图片文件
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10
  
  // 检查文件类型和大小
  if (!isImage) {
    message.error('仅支持JPG、PNG格式文件上传')
    return false
  }
  
  if (!isLt10M) {
    message.error('单个文件大小不能超过10MB')
    return false
  }
  
  // 检查文件列表是否已达到最大数量
  if (fileList.value.length >= 3) {
    message.error('最多只能上传3个文件')
    return false
  }
  
  // 直接返回true，让v-model自动管理fileList
  return true
}

// 自定义上传请求处理函数
const customUploadRequest = (options) => {
  const { file } = options
  
  // 调试信息
  console.log('customUploadRequest called with file:', file)
  
  // 确保raw属性指向原始文件对象
  // 对于Ant Design Vue Upload组件，原始文件通常在originFileObj中
  const originalFile = file.raw || file.originFileObj || file
  
  // 确保file.raw存在且是File对象
  if (!(originalFile instanceof File)) {
    console.error('File raw property is not a File object:', originalFile)
    // 尝试从file对象本身提取原始文件
    if (file instanceof File) {
      file.raw = file
    } else {
      console.error('无法获取有效的原始文件对象:', file)
      // 创建一个新的File对象，确保raw属性存在
      try {
        if (file.size && file.name && file.type) {
          // 只有当file对象包含必要信息时才尝试创建新的File对象
          file.raw = new File([file], file.name, { type: file.type })
        } else {
          console.error('无法创建有效的File对象:', file)
        }
      } catch (createError) {
        console.error('创建File对象失败:', createError)
      }
    }
  } else {
    // 原始文件存在且是File对象，直接使用
    file.raw = originalFile
  }
  
  // 确保file.raw存在
  if (!file.raw) {
    console.error('File raw property is null or undefined:', file)
  }
  
  // 立即设置文件状态为已上传，避免显示"上传中"
  file.status = 'done'
  
  // 为文件生成预览URL
  try {
    if (file.type.startsWith('image/')) {
      // 图片文件：使用FileReader生成预览URL
      const reader = new FileReader()
      reader.onload = (e) => {
        file.preview = e.target.result
        // 立即调用success回调，通知Upload组件上传成功
        options.onSuccess({})
      }
      reader.onerror = (error) => {
        console.error('图片预览URL生成失败:', error)
        // 即使预览URL生成失败，也调用success回调
        options.onSuccess({})
      }
      reader.readAsDataURL(file.raw)
    } else {
      // PDF和其他文件：使用URL.createObjectURL生成预览URL
      try {
        file.preview = URL.createObjectURL(file.raw)
      } catch (urlError) {
        console.error('PDF预览URL生成失败:', urlError)
        // 使用file对象本身作为fallback
        try {
          file.preview = URL.createObjectURL(file)
        } catch (fallbackError) {
          console.error('使用file对象生成预览URL失败:', fallbackError)
          // 移除预览URL，避免后续出错
          delete file.preview
        }
      }
      // 立即调用success回调，通知Upload组件上传成功
      options.onSuccess({})
    }
  } catch (error) {
    console.error('文件处理失败:', error)
    // 即使处理失败，也调用success回调，允许用户继续提交
    options.onSuccess({})
  }
}

// 打开预览模态框 - 使用浏览器自带的预览功能
const openPreviewModal = (file, index) => {
  try {
    let previewUrl = ''
    
    if (file.url) {
      // 已上传到服务器的文件，使用服务器URL
      previewUrl = file.url
    } else if (file.preview) {
      // 本地预览文件，使用生成的预览URL
      previewUrl = file.preview
    } else if (file.raw) {
      // 未上传的本地文件，生成预览URL
      previewUrl = URL.createObjectURL(file.raw)
      // 保存生成的ObjectURL，用于后续清理
      objectUrls.value.push(previewUrl)
    }
    
    if (previewUrl) {
      // 使用浏览器自带的预览功能，在新标签页中打开
      window.open(previewUrl, '_blank')
    } else {
      message.error('无法生成预览URL')
    }
  } catch (error) {
    console.error('预览文件失败:', error)
    message.error('预览文件失败')
  }
}

// 关闭预览模态框
const closePreviewModal = () => {
  previewModalVisible.value = false
  
  // 清理ObjectURL，避免内存泄漏
  if (objectUrls.value.length > 0) {
    objectUrls.value.forEach(url => {
      URL.revokeObjectURL(url)
    })
    objectUrls.value = []
  }
  
  // 重置所有预览状态
  previewFile.value = null
  previewFileIndex.value = null
  previewImageSrc.value = ''
  previewFileName.value = ''
  previewScale.value = 1
  previewRotation.value = 0
}

// 图片旋转
const rotateImage = (degrees) => {
  previewRotation.value += degrees
}

// 图片缩放
const zoomIn = () => {
  if (previewScale.value < 3) {
    previewScale.value += 0.2
  }
}

const zoomOut = () => {
  if (previewScale.value > 0.5) {
    previewScale.value -= 0.2
  }
}

// 重置预览
const resetPreview = () => {
  previewScale.value = 1
  previewRotation.value = 0
}

// 格式化文件大小
const formatFileSize = (size) => {
  if (size < 1024) {
    return size + ' B'
  } else if (size < 1024 * 1024) {
    return (size / 1024).toFixed(1) + ' KB'
  } else {
    return (size / 1024 / 1024).toFixed(1) + ' MB'
  }
}

// 获取文件类型
const getFileType = (fileName) => {
  const ext = fileName.split('.').pop().toLowerCase()
  return ext.toUpperCase() + ' 文件'
}

// 删除文件
const removeFile = (index) => {
  fileList.value.splice(index, 1)
}

const handleSubmit = async () => {
  try {
    console.log('开始提交申请')
    loading.value = true
    
    // 表单验证
    console.log('执行表单验证')
    await formRef.value.validate()
    
    // 额外验证：英语四六级申请必须上传文件
    if ((formData.projectType === 'english_cet4' || formData.projectType === 'english_cet6') && fileList.value.length === 0) {
      message.error('请上传英语成绩报告单')
      return
    }
    
    // 验证：所有申请必须上传文件
    if (fileList.value.length === 0) {
      message.error('请上传证明材料')
      return
    }
    
    // 验证：确保每个文件都已上传完成
    // 对于已存在的文件（编辑模式下从后端获取的文件），跳过raw属性检查
    const uploadingFiles = fileList.value.filter(file => file.status !== 'done' && !file.existing)
    if (uploadingFiles.length > 0) {
      message.error('文件正在上传中，请稍后再提交')
      console.error('正在上传的文件:', uploadingFiles)
      return
    }
    
    // 确保每个文件都有有效的raw属性
    fileList.value.forEach(file => {
      if (!file.existing && !file.raw) {
        console.error('文件缺少raw属性:', file)
        // 尝试修复raw属性
        file.raw = file.raw || file.originFileObj || file
      }
    })
    
    console.log('表单验证通过')
    console.log('fileList内容:', fileList.value.map(file => ({ name: file.name, size: file.size, type: file.type, hasRaw: !!file.raw })))
    
    // 直接使用原始文件列表，不再需要PDF压缩
    const compressedFileList = [...fileList.value]
    
    // 验证：确保每个文件都能被正确处理（添加到FormData）
    console.log('文件列表验证:', compressedFileList.length)
    compressedFileList.forEach((file, index) => {
      console.log(`文件${index}:`, {
        name: file.name,
        type: file.type,
        size: file.size,
        hasRaw: !!file.raw
      })
    })
    
    // 根据项目类型添加特定字段映射
    console.log('当前projectType:', formData.projectType)
    
    // 确保applicationType被正确设置
    // 编辑模式下，优先使用原有申请的类型，避免重新计算导致的类型错误
    let applicationType = ''
    
    // 编辑模式下，直接使用原有申请的类型
    if (isEditMode.value && applicationData.value.application_type) {
      applicationType = applicationData.value.application_type
      console.log('编辑模式下使用原有申请类型:', applicationType)
    } else {
      // 新增申请时，根据项目类型计算applicationType
      // 直接使用后端期望的字符串类型，避免类型转换错误
      if (formData.projectType === 'academic_competition') {
        applicationType = 'academic_competition' // 后端期望的字符串类型
      } else if (formData.projectType === 'ccf_csp') {
        applicationType = 'ccf_csp_certification' // 后端期望的字符串类型
      } else if (formData.projectType === 'english_cet4' || formData.projectType === 'english_cet6') {
        applicationType = 'english_score' // 后端期望的字符串类型，英语四六级统一使用english_score
      } else if (formData.projectType === 'research_achievements' && formData.subProjectType === 'academic_paper') {
        applicationType = 'academic_paper' // 后端期望的字符串类型
      } else if ((formData.projectType === 'patent_work' || 
                  (formData.projectType === 'research_achievements' && formData.subProjectType === 'invention_patent'))) {
        applicationType = 'patent_work' // 后端期望的字符串类型
      } else if (formData.projectType === 'innovation_project') {
        applicationType = 'innovation_project' // 后端期望的字符串类型
      } else if (formData.projectType === 'international_internship') {
        applicationType = 'international_internship' // 后端期望的字符串类型
      } else if (formData.projectType === 'military_service') {
        applicationType = 'military_service' // 后端期望的字符串类型
      } else if (formData.projectType === 'volunteer_service') {
        applicationType = 'volunteer_service' // 后端期望的字符串类型
      } else if (formData.projectType === 'honorary_title') {
        applicationType = 'honorary_title' // 后端期望的字符串类型
      } else if (formData.projectType === 'social_work') {
        applicationType = 'social_work' // 后端期望的字符串类型
      } else if (formData.projectType === 'sports_competition') {
        applicationType = 'sports_competition' // 后端期望的字符串类型
      }
    }
    
    // 确保applicationType始终有值，避免后端报错
    if (!applicationType) {
      console.error('无法确定申请类型，使用默认值')
      applicationType = 'academic_competition' // 默认使用学术竞赛类型，后端期望的字符串类型
    }
    
    // 准备提交数据，使用api.submitApplication方法，该方法会自动处理FormData构建和文件上传
    let title = ''
    
    // 根据不同申请类型生成标题
    if (formData.projectType === 'research_achievements') {
      if (formData.subProjectType === 'academic_paper') {
        title = formData.paper_title || '学术论文加分申请'
      } else if (formData.subProjectType === 'invention_patent') {
        title = formData.patent_title || '发明专利加分申请'
      }
    } else if (formData.projectType === 'academic_competition') {
      title = formData.competition_name || '学术竞赛加分申请'
    } else if (formData.projectType === 'innovation_project') {
      title = formData.project_name || '创新项目加分申请'
    } else if (formData.projectType === 'international_internship') {
      title = '国际组织实习加分申请'
    } else if (formData.projectType === 'military_service') {
      title = '参军入伍加分申请'
    } else if (formData.projectType === 'volunteer_service') {
      if (formData.volunteer_service_type === 'service_hours') {
        title = '志愿时长加分申请'
      } else {
        title = formData.recognition_name || '志愿表彰加分申请'
      }
    } else if (formData.projectType === 'honorary_title') {
      title = formData.honor_name || '荣誉称号加分申请'
    } else if (formData.projectType === 'social_work') {
      title = '社会工作加分申请'
    } else if (formData.projectType === 'sports_competition') {
      title = formData.competition_name || '体育竞赛加分申请'
    } else {
      // 默认标题
      title = '加分申请'
    }
    
    // 确保所有文件都能被正确处理
    // 编辑模式下，从后端获取的文件有existing属性但可能没有raw属性
    const validFileList = compressedFileList.filter(file => file.raw || file.existing)
    if (validFileList.length === 0) {
      message.error('文件上传失败，请重新上传')
      return
    }
    
    // 确保estimated_score始终是合法数字
    const finalEstimatedScore = isEditMode.value ? existingEstimatedScore.value : (estimatedScore.value !== null ? estimatedScore.value : 0)
    
    const submitData = {
      application_type: applicationType,
      title: title,
      user_explanation: '',
      screenshot: compressedFileList, // 传递完整的文件列表
      estimated_score: finalEstimatedScore
    }
    
    // 根据项目类型添加特定字段
    if (formData.projectType === 'academic_competition') {
      // 添加竞赛相关字段
      console.log('添加学术竞赛字段')
      
      // 如果是CCF CSP认证，设置正确的competition_name和competition_specific_name
      if (formData.competition_type === 'csp') {
        // CCF CSP认证：competition_name使用'programming'，competition_specific_name使用'CCF CSP'
        submitData.competition_name = 'programming'
        submitData.competition_specific_name = 'CCF CSP'
      } else {
        // 普通竞赛：competition_name使用用户输入的竞赛名称
        // 注意：这里的competition_name对应后端的competition_specific_name
        submitData.competition_name = 'programming' // 后端需要的竞赛类型，使用默认值
        submitData.competition_specific_name = formData.competition_name // 用户输入的具体竞赛名称
      }
      
      const competitionLevelMap = {
        'a_plus': 'A+',
        'a': 'A',
        'a_minus': 'A-',
        'b_plus': 'B+',
        'b': 'B'
      }
      submitData.competition_level = competitionLevelMap[formData.competition_category] || formData.competition_category
      // 移除不必要的字段，只保留后端需要的字段
      // submitData.award_level = formData.award_level
      // submitData.project_type = formData.project_type
      // submitData.team_size = formData.team_size
      // submitData.team_role = formData.team_role
    } else if (formData.projectType === 'innovation_project') {
      // 添加创新项目相关字段
      console.log('添加创新项目字段')
      submitData.project_name = formData.project_name
      submitData.project_level = formData.project_level
      // 为了兼容后端，添加project_duration字段，使用空字符串作为默认值
      submitData.project_duration = ''
      // is_responsible_person字段可能不需要，或者需要映射为其他字段
      // 根据后端要求，这里只添加必填字段
    } else if (formData.projectType === 'international_internship') {
      // 添加国际组织实习相关字段
      console.log('添加国际组织实习字段')
      // 后端字段映射：organization_name对应前端的institution_name
      submitData.organization_name = formData.institution_name
      // 后端字段映射：internship_duration对应前端的实习时长类型
      submitData.internship_duration = formData.internship_duration_type === 'full_year' ? '满一学年' : '满一学期'
      // 不需要的字段不再提交
    } else if (formData.projectType === 'military_service') {
      // 添加参军入伍相关字段
      console.log('添加参军入伍字段')
      // 后端字段映射：根据服兵役时长类型设置相应的日期
      // 生成当前日期前的适当日期作为入伍和退伍时间
      const currentDate = new Date()
      let startDate, endDate
      
      if (formData.military_service_duration === 'one_to_two_years') {
        // 一年以上（含一年）、两年以内
        startDate = new Date(currentDate.getFullYear() - 2, currentDate.getMonth(), currentDate.getDate())
        endDate = new Date(currentDate.getFullYear() - 1, currentDate.getMonth(), currentDate.getDate())
      } else {
        // 两年以上（含两年）
        startDate = new Date(currentDate.getFullYear() - 3, currentDate.getMonth(), currentDate.getDate())
        endDate = new Date(currentDate.getFullYear() - 1, currentDate.getMonth(), currentDate.getDate())
      }
      
      // 格式化日期为YYYY-MM-DD格式
      const formatDate = (date) => {
        return date.toISOString().split('T')[0]
      }
      
      submitData.service_start_date = formatDate(startDate)
      submitData.service_end_date = formatDate(endDate)
      // 不再需要military_unit字段，根据用户需求移除
      // submitData.military_unit = formData.military_unit
      submitData.military_unit = '' // 提供默认空字符串，避免后端验证失败
    } else if (formData.projectType === 'volunteer_service') {
      // 添加志愿服务相关字段
      console.log('添加志愿服务字段')
      // 格式化日期为YYYY-MM-DD格式
      const formatDate = (date) => {
        return date ? date.toISOString().split('T')[0] : ''
      }
      
      // 根据服务类型添加不同字段
      if (formData.volunteer_service_type === 'service_hours') {
        // 志愿服务（时长）
        submitData.service_type = 'hours'
        submitData.working_hours = formData.service_hours // 后端期望的字段名是working_hours
        submitData.activity_name = '志愿时长加分申请' // 使用固定的activity_name
        // 添加activity_date字段，后端必填
        submitData.activity_date = formatDate(new Date()) // 使用当前日期作为activity_date
      } else if (formData.volunteer_service_type === 'recognition') {
        // 志愿表彰
        submitData.service_type = 'recognition'
        submitData.activity_name = formData.recognition_name || '志愿表彰加分申请'
        submitData.activity_date = formatDate(new Date()) // 使用当前日期作为activity_date
      }
    } else if (formData.projectType === 'honorary_title') {
      // 添加荣誉称号相关字段
      console.log('添加荣誉称号字段')
      // 根据用户需求，荣誉称号申请应该填写：荣誉名称，荣誉级别，授予学年，是否是集体荣誉
      // 后端期望的字段名映射
      submitData.title_name = formData.honor_name // 后端期望的字段名是title_name
      submitData.awarding_organization = '未知' // 后端期望的字段名是awarding_organization，提供默认非空值
      // 将授予学年转换为授予日期（使用该学年的1月1日）
      const awardingYear = formData.awarding_year
      if (awardingYear) {
        submitData.awarding_date = `${awardingYear}-01-01`
      } else {
        submitData.awarding_date = new Date().toISOString().split('T')[0] // 后端期望的字段名是awarding_date，使用当前日期
      }
      submitData.honor_level = formData.honor_level
      submitData.awarding_year = formData.awarding_year
      submitData.is_collective = formData.is_collective
      // 后端可能使用level字段表示荣誉级别
      submitData.level = formData.honor_level
    } else if (formData.projectType === 'social_work') {
      // 添加社会工作相关字段
      console.log('添加社会工作字段')
      // 后端期望的字段名映射
      submitData.organization = '未知' // 后端期望的字段名是organization，提供默认非空值"未知"
      submitData.work_period = formData.term_years // 后端期望的字段名是work_period，使用任期年数
      submitData.position = formData.position_name // 职务名称，后端字段名为position
      submitData.teacher_score = formData.teacher_score // 老师打分
      submitData.work_description = '' // 工作描述，提供默认空字符串
      submitData.activity_date = new Date().toISOString().split('T')[0] // 使用当前日期作为activity_date
    } else if (formData.projectType === 'sports_competition') {
      // 添加体育竞赛相关字段
      console.log('添加体育竞赛字段')
      // 后端期望的字段名映射
      submitData.competition_name = formData.competition_name // 竞赛名称
      submitData.competition_level = formData.competition_level // 竞赛级别
      submitData.achievement = formData.award_level // 获奖等级
      submitData.is_team_project = formData.is_team_project === 'true' // 是否是团队项目
      
      if (formData.is_team_project === 'true') {
        // 团队项目：添加团队成员数字段
        submitData.team_size = formData.team_size // 团队成员数
        submitData.project_type = '' // 团队项目不需要project_type，使用空字符串
      } else {
        // 非团队项目：添加项目类型字段
        submitData.team_size = 1 // 非团队项目成员数为1
        submitData.project_type = formData.project_type // 项目类型（单人项目、二人项目）
      }
      
      // 添加竞赛日期字段，使用当前日期
      submitData.competition_date = new Date().toISOString().split('T')[0]
      // 添加必要的默认字段
      submitData.user_explanation = '' // 提供默认空字符串，避免后端验证失败
      
      // 根据竞赛级别映射到后端level字段的合法选项
      // 后端level字段的合法选项：national, provincial, university, college
      let levelMapping = {
        'international': 'national', // 国际级映射为国家级
        'national': 'national', // 国家级映射为国家级
        'provincial': 'provincial', // 省级映射为省级
        'school': 'university' // 校级映射为校级
      }
      submitData.level = levelMapping[formData.competition_level] || '' // 只发送后端接受的合法值
    } else if (formData.projectType === 'english_cet4' || formData.projectType === 'english_cet6') {
      // 添加英语四六级相关字段
      console.log('添加英语四六级字段')
      // 后端期望的字段名映射
      submitData.exam_score = formData.exam_score // 考试成绩
      // 添加必要的默认字段
      submitData.user_explanation = '' // 提供默认空字符串，避免后端验证失败
    } else if (formData.projectType === 'academic_paper' || (formData.projectType === 'research_achievements' && formData.subProjectType === 'academic_paper')) {
      // 添加学术论文相关字段
      console.log('添加学术论文字段')
      // 后端期望的字段名映射
      submitData.title = formData.paper_title // 论文标题，后端期望的字段名是title
      submitData.paper_title = formData.paper_title // 同时保留paper_title字段，确保兼容性
      submitData.journal_category = formData.journal_category
      submitData.is_independent_author = formData.is_independent_author
      submitData.is_co_first_author = formData.is_co_first_author
      submitData.author_rank = formData.author_rank
      submitData.is_xmu_first_unit = formData.is_xmu_first_unit
      submitData.author_type = formData.author_type || 'author' // 确保author_type字段被提交
      // 添加必要的默认字段
      submitData.user_explanation = '' // 提供默认空字符串，避免后端验证失败
    } else if (formData.projectType === 'patent_work' || formData.subProjectType === 'invention_patent') {
      // 添加专利相关字段
      console.log('添加专利字段')
      // 后端期望的字段名映射
      submitData.title = formData.patent_title // 专利标题，后端期望的字段名是title
      submitData.patent_title = formData.patent_title // 同时保留patent_title字段，确保兼容性
      submitData.author_type = formData.author_type || 'inventor' // 确保author_type字段被提交
      submitData.is_xmu_first_unit = formData.is_xmu_first_unit || 'true' // 确保is_xmu_first_unit字段被提交
      // 添加必要的默认字段
      submitData.user_explanation = '' // 提供默认空字符串，避免后端验证失败
    }
    
    console.log('提交数据：', submitData)
    
    // 根据是否是编辑模式调用不同的API方法
    console.log('调用API方法，编辑模式：', isEditMode.value)
    try {
      // 添加上传进度回调
      const submitDataWithProgress = {
        ...submitData,
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            // 计算上传进度百分比
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            console.log(`上传进度：${percentCompleted}%`)
            // 可以在这里添加进度条更新逻辑
          }
        }
      }
      
      let response
      if (isEditMode.value) {
        // 编辑模式：调用editApplication方法
        console.log('调用api.editApplication方法，ID：', applicationId.value)
        response = await api.editApplication(applicationId.value, submitDataWithProgress)
      } else {
        // 新增模式：调用submitApplication方法
        console.log('调用api.submitApplication方法')
        response = await api.submitApplication(submitDataWithProgress)
      }
      
      console.log('API Response:', response)
      
      if (response && (response.id || response.success)) {
        console.log('申请提交成功')
        message.success(isEditMode.value ? '申请编辑成功' : '申请提交成功')
        router.push('/student/applications')
      } else {
        console.log('申请提交失败，响应数据：', response)
        message.error(response?.message || response?.error || (isEditMode.value ? '申请编辑失败' : '申请提交失败'))
      }
    } catch (error) {
      console.error('API Request Error:', error)
      console.error('Error response:', error.response)
      console.error('Error status:', error.response?.status)
      console.error('Error data:', error.response?.data)
      console.error('Error message:', error.message)
      message.error(`${isEditMode.value ? '申请编辑失败' : '申请提交失败'}：${error.message || '服务器返回格式错误'}`)
    }
  } catch (error) {
    console.error('提交失败:', error)
    message.error('提交失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 重置表单
const handleReset = () => {
  formRef.value.resetFields()
  fileList.value = []
}

// 厦门大学是否为第一单位验证（适用于学术论文和发明专利）
const validateXmuFirstUnit = (_, value) => {
  // 检查是否为学术论文或发明专利申请
  if ((formData.projectType === 'academic_paper' || formData.subProjectType === 'invention_patent') && value === 'false') {
    return Promise.reject(new Error('学术论文和发明专利申请中，厦门大学必须为第一单位'))
  }
  return Promise.resolve()
}

// 文件上传验证 - 确保至少上传一个文件
const validateFileUpload = (_, value) => {
  // 仅当项目类型为英语四六级时才验证文件上传
  if ((formData.projectType === 'english_cet4' || formData.projectType === 'english_cet6') && fileList.value.length === 0) {
    return Promise.reject(new Error('请上传英语成绩报告单'))
  }
  return Promise.resolve()
}
</script>

<style scoped>
.upload-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  text-align: center;
  margin-bottom: 20px;
  font-size: 24px;
  font-weight: 600;
}

.upload-card {
  margin-bottom: 20px;
}

.upload-form {
  max-width: 800px;
  margin: 0 auto;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-actions {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  gap: 16px;
}

.score-preview {
  margin: 20px 0;
}

.file-preview-list {
    margin-top: 16px;
    display: flex;
    flex-wrap: wrap;
}
</style>