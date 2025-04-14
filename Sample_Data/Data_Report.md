# Data Report

## 1 Data Preprocessing

The data provided by the NFL Big Data Bowl was already clean and structured. But, in order to use given, non-numeric fields, in any further analysis, we had to use a combination of either label encoding or one hot encoding, based on the qualities of each feature, to run it through any modeling or visualizations. Out of 122 total fields that are provided to us, 44 of them were non-numeric, while the remaining 78 were numeric and ready for use in most analytical contexts. Many of these non-numeric fields included categorical variables like team abbreviations, formations, or route types. Any specific data manipulation that was performed was driven by feature engineering needs, specifically to design and extract the features we intended to analyze. Those case-by-case manipulations are discussed further below.

For the feature that vectorizes the exact path of each defensive player after the line is set, a lot of normalizations had to be made to ensure that there are no biases based on player position on the field. First, the spatial coordinates (x, y) were normalized to a consistent scale no matter which direction of the play or the yard line the player is at. Then, player movement and orientation data were resample to a fixed number of steps per play, creating uniform time series vectors that are able to be compared between players, Orientation angles were also converted into unit vectors to eliminate circular bias (i.e. understanding that 359 and 1 degree are actually very close to each other).

## 2 Feature Extraction

1. **Late Defensive Movements:** This feature is calculated by analyzing player tracking data to quantify movement just before the snap. A late shift is defined as movement occurring within a few seconds before the snap (about 2 seconds before). Currently, all given data is on player level, therefore, I’m working on creating features that will represent the late shifts in play level. This is a very important feature because a high late shift may indicate pre-snap motion strategies such as a receiver in motion or a defensive shift in response to offensive alignment.

2. **Nearest Defender to Each Receiver at the Snap:** This feature evaluates the closest defender to each receiver at the ‘SNAP’ time frame. The receiver is essential at the SNAP as the quarterback who has the ball will most likely be throwing the ball to players in this specific position. Determining who the nearest defenders are to this position helps to see how good the defense reads the offensive and what play they were aiming to do during ‘BEFORE SNAP’ time. If defenders are far away from the receiver, then that means the defense didn’t read the offense that well. Vice versa if all the receivers are heavily guarded by defenders, then the defense reads the offense play correctly. In order to calculate this feature per play, we have to find the absolute difference between each defender-receiver scenario. We have the players position data given as features x and y, respectively. So we take the absolute difference between the defenders x position and receivers x position, and the same thing for the y position of both players. Then we add those absolute differences in x and y position together, and whichever defender has the lowest number with a certain receiver is the nearest defender to that specific receiver. 

3. **Defensive Player Movement Through the Snap:** This feature is calculated by running through each play of every game, and printing how the number of defensive players moving through the snap. The feature can calculate different outcomes by changing the frame. Meaning it can calculate one second through the snap, two seconds, and so on. 


4. **Defensive Reaction to Offensive Motion:** In my analysis of defensive reactions to offensive pre-snap motion, I am leveraging player tracking data to quantify how defenders adjust to shifts and motions. The process begins by identifying offensive players who go into motion, which I’ve accomplished using the shiftSinceLineset and motionSinceLineset features provided in the dataset. Next, I determine the frames where motion starts and ends by analyzing the offensive player’s velocity. Squaring the velocity and plotting it over frames reveals clear patterns, motion begins with a sudden velocity spike and ends with a sudden drop, making it easy to pinpoint the motion window. The next step is identifying which defensive players react to the offensive motion. This process is divided into two approaches based on the pff_manZone feature: one for man coverage and another for zone coverage. In man coverage, only one defender should follow the motioning player. I determine this player by comparing their velocity and directional data relative to the offensive players. If their movement similarity surpasses a defined threshold for motioning frames, they are identified as the defender responsible for tracking the motion. For zone coverage, multiple defenders may adjust their positioning in response to motion. Instead of assigning a single defender for the entire sequence, I break the play into time segments and compare each defender’s similarity to the offensive motion in each segment. If one defender exhibits the highest similarity in a given segment but another defender takes over in the next, this signals a coverage switch—a common characteristic of zone defense.

## 3 and 4 Feature Trends and Analysis:
Each feature was analyzed by separating all plays into three quantile groups based on the amount of that feature. Within each group, I calculated the average yards gained, average expected points added (EPA), the percentage of big yardage plays (15+ yards), and the percentage of big EPA plays (EPA > 1.5). In addition to the quantile analysis, I also compared the bottom 100 and top 100 plays for each feature. The sections below summarize the trends observed from these comparisons.

1. Late Defensive Movements

    1.1 For teamTotalDistance (the total distance defenders moved in the last two seconds before the ball was snapped), there was a clear trend: as defensive movement increased, both the average yards gained and average EPA decreased. The more the defense moved the worse the offense did.

    * Plays where defenders moved less (< 25th percentile) saw an average EPA of -0.018 and 5.69 yards gained.

    * Plays with moderate defensive movement (25th–75th percentile) saw a slightly lower EPA of -0.029 and 5.48 yards gained.

    * Plays with the highest defensive movement (> 75th percentile) resulted in the lowest EPA at -0.046 and the fewest yards gained at 5.37 yards.

    This suggests that greater defensive movement just before the snap may disrupt offensive plays, slightly lowering offensive efficiency and yardage. More defensive movement could mean they read the offensive play or a blitz.




    1.2 For teamTotalSpeed (the total average speed defenders moved at 2 seconds before the snap), the trend was very similar, maybe not as strong.

    * Plays where defenders moved the slowest (< 25th percentile) saw an average EPA of -0.011 and 5.61 yards gained.

    * Plays with moderate defensive speed (25th–75th percentile) had an average EPA of -0.038 and 5.49 yards gained.

    * Plays with the highest defensive speed (> 75th percentile) had an EPA of -0.035 and 5.43 yards gained.

    This suggests that higher defensive speed before the snap may slightly disrupt offensive plays, lowering both average yards gained and offensive efficiency (EPA).
    At first, this result seems a little surprising — greater defensive distance and speed during late shifts actually correlated with better defensive outcomes. This could suggest that the defense was reacting quickly and effectively to offensive motion, or that defenders had picked up on offensive tendencies and adjusted accordingly. On the other hand, less movement before the snap might indicate a lack of recognition or hesitation, where the defense is slower to react or unsure of the offensive formation. 


    I refined the feature by applying thresholds: only defenders with a total distance greater than 5 or an average speed greater than 5 were included. This adjustment filtered out defenders making normal or minimal movements (e.g., moving at 3 velocity), and focused on defenders exhibiting more significant motion (e.g., moving at 5 velocity or faster). After applying these thresholds, the same general trend remained — greater defensive movement correlated with slightly better defensive outcomes — but the effect was not as strong as before.

2. Distance to Nearest Receiver

    2.1 For maxDistance (the maximum distance between a defender and the nearest receiver), this trend emerged:

    * As maxDistance increased, the offense gained slightly more yards (5.02 ➔ 5.58 ➔ 5.67), but EPA became more negative (-0.014 ➔ -0.024 ➔ -0.055).

    * Rates of big yardage plays (over 15 yards) and big EPA plays (over 1.5 EPA) stayed relatively constant across quantiles.

    * The top 100 plays (with the greatest total distance) showed significantly higher average yards gained compared to the bottom 100, but had a lower average EPA. This trend makes sense: when defenders are positioned farther back, it likely reflects a deliberate defensive strategy to allow shorter gains while preventing big, high-impact plays, rather than confusion or blown coverages.
    
    This suggests that larger gaps between defenders and receivers may allow more yards to be gained, but they do not necessarily translate into bigger-impact plays or higher EPA for the offense. In fact, EPA became slightly more negative, possibly indicating more stops despite slightly higher yardage. 


    2.2 For averageDistance (the average distance between defenders and their assigned receivers), a similar trend was observed: 

    * As averageDistance increased, yards gained steadily rose (5.15 ➔ 5.56 ➔ 5.64), while EPA became increasingly negative (-0.017 ➔ -0.028 ➔ -0.049).
    * Big yardage play rates remained flat (~10%), and big EPA play rates slightly declined (from 13% ➔ 9%).
    * This indicates that wider defensive spacing may allow slightly more yards, but may also limit high-EPA plays, possibly due to defenders playing off coverage and making safer tackles after catches.
    
    Overall, the distance between a receiver and their defender appears to have little impact on the outcome of a play. Larger gaps do not necessarily indicate defensive confusion, nor do they consistently lead to better results for the offense. Instead, they likely reflect different defensive strategies based on the specific game situation.

3. Defensive Motion Through Snap

    3.1 For numDefendersMoving (the number of defenders moving through the snap window), the results were interesting.

    * Plays with more defenders moving (> 75th percentile) saw slightly more yards gained (5.74), but a more negative EPA (-0.039) compared to plays with fewer defenders moving.

    * Big yardage and big EPA play rates stayed relatively flat across the quantiles, but slightly declined with more movement.

    This suggests that defenders moving through the snap window may not necessarily be a sign of confusion. Instead, it could reflect defenders reacting to offensive motion, adjusting to formations, or actually anticipating the play. This movement might suggest the defender has read the play correctly.

    3.2 For maxSpeedThroughSnap (the maximum speed of defenders during the snap window), the results were less clear than with other movement features:

    * Across quantiles, there was no strong, consistent relationship between maximum defender speed and offensive success.
    * Plays with faster maximum speeds saw slightly fewer yards gained and slightly more negative EPA, but the differences were small.
    * Big play rates (both yardage and EPA) remained mostly unchanged regardless of defender speed.

    These results suggest that maximum speed alone may not strongly impact play outcomes, but when defenders move at higher velocities, it could reflect greater defensive confidence or aggressiveness, possibly limiting offensive production slightly.

    Overall, defender movement through the snap does not necessarily indicate confusion. It could reflect a designed blitz, a strong defensive read, or a coordinated adjustment to the offensive formation.

4. Reaction to Offensive Motion:

    Offensive motion before the snap was associated with better play outcomes.

    * When at least one offensive player went into motion, plays averaged 6.5 yards gained and an average EPA of 0.065.
    * In contrast, plays without any offensive motion averaged only 5.17 yards gained and an average EPA of -0.055.

    To address this, only plays where at least one offensive player went into motion were used in the calculations.

    4.1 For segSwitchCount (number of times the top defender changed during a motion event), there was a relationship that suggested confusion. 

    * As the number of reacting defenders increased, both yards gained and EPA steadily rose.

    * Plays in the top 75th percentile for defender reactions averaged 7.24 yards and an EPA of 0.086, compared to 6.23 yards and an EPA of 0.068 when few defenders reacted.

    Looking specifically at the top and bottom 100 plays:

    * Plays with the highest number of defender reactions had a much stronger average EPA (0.155) and gained 6.89 yards on average.
    * In contrast, plays with the fewest defender reactions averaged only 5.16 yards and barely positive EPA (0.005).
    
    This suggests that when defenders switch between who's following the player in motion, it may create confusion or misalignment in the defense, leading to more successful offensive plays.
    
    4.2 For numDefendersReact (the number of defenders that reacted to a player in motion), plays 
    
    where more defenders reacted showed a modest positive impact on offensive outcomes:
    
    In the quantile analysis, yards gained generally increased with more defenders reacting (6.22 ➔ 6.76 ➔ 6.61), while EPA was positive across all groups, although slightly lower for the highest reaction group.
    
    Looking at the top and bottom 100 plays:
    
    * Plays with the most defenders reacting (top 100) had the highest EPA (0.131) and gained 6.69 yards on average.
    * Plays with the fewest defenders reacting (bottom 100) had a negative EPA (-0.031) and only 5.12 yards gained.
    
    These results suggest that when multiple defenders react to a single motion there may have been a miscommunication. Offenses often perform better when they provoke a strong defensive reaction.
    
    4.3 For totalMotionDuration (the total frames a defender spent tracking a player in motion), plays where defenders tracked offensive motion for longer durations were associated with better offensive outcomes:

    * As the total tracking duration increased, yards gained and EPA both rose.
    Plays in the top 75th percentile for motion tracking averaged 6.51 yards and an EPA of 0.090, compared to only 6.16 yards and an EPA of 0.002 when defenders tracked motion for shorter periods.
    
    Looking specifically at the top and bottom 100 plays:
    * Plays with the longest defender tracking (top 100) resulted in the highest average EPA (0.156) and 7.11 yards gained.
    * Plays with the shortest tracking durations (bottom 100) had a negative EPA (-0.045) and only 5.53 yards gained.
    
    These results suggest that longer defensive tracking during pre-snap motion often favors the offense, possibly by creating confusion, hesitation, or alignment issues in the defense.
    
    4.4 For avgSimilarityScore (how closely defenders mirrored offensive motion), higher similarity scores — meaning defenders more closely mirrored offensive motion — were associated with better offensive outcomes:
    
    * As avg_sim_score increased, EPA and big play rates steadily rose.
    * Plays with the highest average similarity had an EPA of 0.103 and slightly lower yards gained compared to the middle group, but significantly higher big EPA play rates.
    
    Looking at the extremes:
    
    * The top 100 plays with the highest average similarity had an average EPA of 0.356 and gained 7.91 yards per play. Additionally, 17% of these plays resulted in gains of 15 yards or more, and 28% produced an EPA greater than 1.5.
    
    This suggests that when defenders tightly track offensive motion, they may actually be overcommitting or taking the bait, allowing offenses to exploit space elsewhere.
    Interestingly, even the bottom 100 plays (lowest average similarity) showed better offensive results than the middle quartiles, with an EPA of 0.108, 6.84 yards gained, and 18% of plays achieving an EPA greater than 1.5.

    This suggests that both very tight and very poor defensive tracking may create vulnerabilities 
    for the defense, either by overcommitting to motion or failing to stay aligned.
    
    4.5 For maxSimilarityScore (highest similarity score for a defender that play), a similar pattern appeared:
    
    * Higher max similarity correlated with higher offensive EPA and more big plays.
    
    * While the middle quantile (25–75%) had slightly better yards gained (6.61), the highest quantile showed a jump in big EPA plays (16%). 

    Looking at the extremes:
     
    * The top 100 plays with the highest max similarity had an EPA of 0.353 and averaged 7.88 yards gained. Additionally,  28% of the plays produced an EPA greater than 1.5.
    This again supports the idea that tight defensive tracking of motion may open up offensive opportunities if defenders overcommit.

    4.5 For varSimilarityScore (variance between similarity scores of each defenders tracking), higher variance in defender tracking behavior was also associated with more successful offensive plays:
    
    * Plays with the most consistent defender tracking (lowest variance group) still had a higher EPA (0.102) than the middle group, despite slightly lower yards gained (6.17 yards).
    * Plays in the highest variance group had higher EPA (0.105) and more yards gained (6.82) compared to lower variance groups.
    
    Looking at the extremes:
    
    * The top 100 plays with the highest tracking variance had the highest average EPA (0.441) and 
    gained 8.96 yards per play. Massive offensive success.
    
    This suggests that inconsistent defender reactions to motion, or large variance in tracking, may create bigger breakdowns and more explosive offensive opportunities. It also still hints that super tight tracking could mean defenders fell for the motion.
    
    Overall, offensive motion is strongly associated with better outcomes for the offense. Plays with more players put into motion, as well as more total motion events (such as a player motioning multiple times), consistently led to higher yards gained and EPA. When focusing on the defensive response, the longer defenders spent tracking motion, the better the offense performed. Similarly, plays where more defenders reacted to the motion also resulted in greater offensive success. Even when defenders tightly mirrored the motion, showing stronger similarity scores, offenses continued to perform better, suggesting that motion can bait defenders into overcommitting or create mismatches that the offense can exploit.

## 5 Issues

Based on the data exploration and feature analysis, several issues could arise in later stages of the project.

* Not all engineered features show a meaningful relationship with defensive confusion; some features have little to no correlation, while others show opposite trends than expected. This means careful feature selection will be necessary to build an accurate confusion score.

* Many of the strongest features are specifically tied to offensive motion plays. This may limit the model's ability to assess confusion accurately on plays without motion, potentially requiring separate treatment for different play types or additional feature development.

* The features provided directly by the NFL may dominate feature importance in our models, which could overshadow or devalue our engineered features, potentially leading to biased or less interpretable results.

Overall, while there are clear signals in some features, there is a risk that the available data may not fully capture defensive confusion across all situations.
