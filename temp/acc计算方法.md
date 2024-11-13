贝叶斯估计的具体计算方法基于**贝叶斯统计**原理，结合了**先验分布**与**观测数据**来得出更稳健的概率估计。下面我会详细讲解这种方法是如何应用于掌握程度估计的。

### 1. 公式概述

掌握程度的贝叶斯估计通常可以用**Beta分布**来描述。因为正确率是一个介于 0 和 1 之间的概率问题，Beta分布是常用的先验分布。基本公式如下：

#### 贝叶斯后验分布公式：
\[
P(\theta | X) = \frac{P(X | \theta) P(\theta)}{P(X)}
\]
其中：
- \(\theta\) 是你想要估计的正确率（掌握程度）。
- \(P(\theta)\) 是先验分布，假设为 Beta 分布。
- \(P(X|\theta)\) 是似然函数，即基于观测数据的正确率。
- \(P(\theta | X)\) 是后验分布，即在观测了数据之后对掌握程度的更新估计。

#### Beta 分布
Beta 分布的形式如下：
\[
P(\theta; \alpha, \beta) = \frac{\theta^{\alpha-1}(1-\theta)^{\beta-1}}{B(\alpha, \beta)}
\]
其中：
- \(\alpha\) 和 \(\beta\) 是 Beta 分布的两个参数，\(\alpha\) 表示“成功次数 + 1”（正确的题目数 + 1），\(\beta\) 表示“失败次数 + 1”（错误的题目数 + 1）。
- \(B(\alpha, \beta)\) 是 Beta 函数，归一化常数。

### 2. 先验分布的选择

**先验分布**用于反映我们在观测数据之前对正确率的初步假设。假设题目的初始掌握情况为：
- 设定一个先验值，比如认为一开始所有版块的掌握情况是50%（即 Beta(1, 1) 分布）。
  
这相当于说我们初始假设正确题目和错误题目的比例是1:1。

### 3. 更新后验分布

根据观测到的正确题目数和错误题目数，通过似然函数将先验分布更新为后验分布。

- 假设某个版块有 \(k\) 道题目，其中 \(s\) 道题做对了，\(f = k - s\) 道题做错了。
- 使用观测到的数据更新先验分布，更新后的参数为：
  \[
  \alpha_{\text{posterior}} = \alpha_{\text{prior}} + s
  \]
  \[
  \beta_{\text{posterior}} = \beta_{\text{prior}} + f
  \]
  这里的 \(s\) 是做对的题目数，\(f\) 是做错的题目数，\(\alpha_{\text{prior}} = 1\)，\(\beta_{\text{prior}} = 1\)。

### 4. 计算后验均值（掌握程度的估计）

Beta 分布的后验均值可以作为我们对正确率的贝叶斯估计：
\[
\hat{\theta} = \frac{\alpha_{\text{posterior}}}{\alpha_{\text{posterior}} + \beta_{\text{posterior}}}
\]

所以，对于每个版块的掌握程度，贝叶斯估计为：
\[
\hat{\theta} = \frac{1 + s}{1 + s + 1 + f} = \frac{1 + s}{2 + k}
\]

- 当 \(k\) 很大时，贝叶斯估计值接近于简单的正确率 \(s/k\)。
- 当 \(k\) 较小时，贝叶斯估计将趋向先验分布的值（比如50%）。

### 5. 示例计算

#### 原始数据：
- **全书**：435/579=75.1%
  - \(s = 435\)，\(f = 579 - 435 = 144\)
  - 贝叶斯估计：\[
  \hat{\theta} = \frac{1 + 435}{2 + 579} = \frac{436}{581} \approx 0.7923
  \]
- **空间解析几何**：14/14=100%
  - \(s = 14\)，\(f = 0\)
  - 贝叶斯估计：\[
  \hat{\theta} = \frac{1 + 14}{2 + 14} = \frac{15}{16} = 0.9375
  \]

#### 为什么题目少时估计较低？
题目少时，贝叶斯估计不会给出100%或0%的极端值，而是更偏向于先验分布。比如对于空间解析几何，虽然原始正确率是100%，贝叶斯估计为93.75%，是因为贝叶斯估计考虑到了题目数较少带来的不确定性。

### 6. 代码实现

```python
import pandas as pd
import re

class AccuracyEstimator:
    def __init__(self, md_file_path):
        self.df_list = self._extract_tables(md_file_path)

    def _extract_tables(self, md_file_path):
        """从markdown文件中提取表格并存入dataframe"""
        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找<div class="acc-table">标签包裹的内容
        tables = re.findall(r'<div class="acc-table">(.+?)</div>', content, re.S)
        
        df_list = []
        for table in tables:
            # 处理表格字符串，将其转换为dataframe
            df = pd.read_html(table)[0]
            df_list.append(df)
        return df_list

    def bayesian_estimate(self, correct, total, alpha_prior=1, beta_prior=1):
        """根据贝叶斯估计计算掌握程度"""
        s = correct
        f = total - correct
        posterior_alpha = alpha_prior + s
        posterior_beta = beta_prior + f
        return posterior_alpha / (posterior_alpha + posterior_beta)

    def estimate_mastery(self):
        for df in self.df_list:
            for column in df.columns[3:]:
                correct_total = df[column].str.split('=', expand=True)
                correct = pd.to_numeric(correct_total[0], errors='coerce')
                total = pd.to_numeric(correct_total[1], errors='coerce')
                
                # 使用贝叶斯估计计算掌握程度
                df[column + '_mastery'] = self.bayesian_estimate(correct, total)
        return self.df_list

# 使用
estimator = AccuracyEstimator('data/正确率.md')
df_list = estimator.estimate_mastery()

# 查看计算结果
for df in df_list:
    print(df)
```

这个代码实现了：
1. 从Markdown文件中提取表格并存入`self.df_list`中。
2. 使用贝叶斯估计方法对掌握程度进行估算，并根据题目数量和正确率进行调整。