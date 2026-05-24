- Github (3 stars): https://github.com/hongha5192-bit/AlphaAgent
- [Submitted on 24 Feb 2025 (v1), last revised 9 Jun 2025 (this version, v2)]
- AlphaAgent: LLM-Driven Alpha Mining with Regularized Exploration to Counteract Alpha Decay
  - https://arxiv.org/abs/2502.16789

阿尔法挖掘（Alpha mining）作为量化投资的关键环节，致力于在日益复杂的金融市场中发掘能够预测资产未来收益的信号。然而，阿尔法衰退（Alpha decay）——即因子随时间推移丧失预测能力——这一普遍存在的问题，给阿尔法挖掘带来了严峻挑战。传统方法（如遗传编程）常因过拟合和模型复杂性面临快速的阿尔法衰退；而以大语言模型（LLM）为驱动的方法，尽管前景广阔，却往往过度依赖既有知识，导致生成的因子趋于同质化，进而加剧交易拥挤并加速衰退。

为应对这一挑战，我们提出了 AlphaAgent——一个将 LLM 智能体（Agent）与针对性正则化约束有机结合的自主框架，旨在挖掘具备抗衰退能力的阿尔法因子。AlphaAgent 引入了三大核心机制：（i）原创性强制：基于抽象语法树（AST）计算相似度，剔除与现有因子雷同的构造；（ii）假设-因子对齐：通过 LLM 评估市场假说与生成因子之间的语义一致性；（iii）复杂度控制：利用 AST 结构约束限制因子复杂度，防止出现过工程化（Over-engineered）且易过拟合的结构。这三大机制共同引导阿尔法生成过程，在原创性、金融逻辑合理性以及对市场动态演变的适应性之间取得平衡，从而降低阿尔法衰退的风险。

大量实验评估表明，无论是在牛市还是熊市，AlphaAgent 在缓解阿尔法衰退方面均优于传统方法及基于 LLM 的方案。在过去四年中，该系统在中国中证500及美国标普500市场中持续输出显著的阿尔法收益。值得注意的是，AlphaAgent 展现了卓越的抗衰退能力，极大地提升了挖掘强劲因子的潜力。

