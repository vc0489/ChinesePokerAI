CREATE TABLE random_dealt_hands 
(
  GameID BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
  DealtHandStr CHAR(52) NOT NULL, 
  TimeAdded TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- SplitStr e.g. 1232312323123
CREATE TABLE feasible_hand_splits
(
  SplitID BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  GameID BIGINT NOT NULL,
  SeatID TINYINT NOT NULL,
  SplitSeqNo SMALLINT NOT NULL,
  SplitStr CHAR(13) NOT NULL,
  TimeAdded TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  DateGenerated DATE NOT NULL,
  UNIQUE INDEX (GameID, SeatID, SplitSeqNo, DateGenerated),
  FOREIGN KEY (GameID) 
    REFERENCES random_dealt_hands(GameID)
    ON DELETE CASCADE
)

-- Comment
CREATE TABLE split_set_codes
(
  SplitID BIGINT NOT NULL,
  SetNo TINYINT NOT NULL,
  L1Code TINYINT NOT NULL,
  L2Code TINYINT NOT NULL,
  L3Code TINYINT DEFAULT NULL,
  L4Code TINYINT DEFAULT NULL,
  L5Code TINYINT DEFAULT NULL,
  L6Code TINYINT DEFAULT NULL,
  TimeAdded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE INDEX (SplitID, SeatID, SetNo),
  FOREIGN KEY (SplitID)
    REFERENCES feasible_hand_splits(SplitID)
    ON DELETE CASCADE
)




-- StrategyTypeID = 1: WeightedPercentiles
CREATE TABLE split_strategy_types
(
  StrategyTypeID SMALLINT NOT NULL PRIMARY KEY,
  Description VARCHAR(100),
  TimeAdded TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

CREATE TABLE split_strategies
(
  StrategyID SMALLINT NOT NULL PRIMARY KEY,
  StrategyTypeID SMALLINT NOT NULL,
  StrategyName VARCHAR(100),
  TimeAdded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (StrategyTypeID)
    REFERENCES split_strategy_types(StrategyTypeID)
)


-- SetNo = 0 means full score
CREATE TABLE split_scores
(
  StrategyID SMALLINT NOT NULL,
  SplitID BIGINT NOT NULL,
  SeatID TINYINT NOT NULL,
  SetNo TINYINT NOT NULL,
  Score DOUBLE PRECISION,
  TimeAdded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE INDEX (StrategyID, SplitID, SeatID, SetNo),
  FOREIGN KEY (SplitID)
    REFERENCES feasible_hand_splits(SplitID)
    ON DELETE CASCADE,
  FOREIGN KEY (StrategyID)
    REFERENCES split_strategies(StrategyID)
    ON DELETE CASCADE
)

CREATE TABLE code_percentiles
(
  PoolSize TINYINT NOT NULL,
  SetSize TINYINT NOT NULL,
  CodeMaxLevel TINYINT NOT NULL,
  L1Code TINYINT NOT NULL,
  L2Code TINYINT NOT NULL,
  L3Code TINYINT DEFAULT NULL,
  L4Code TINYINT DEFAULT NULL,
  L5Code TINYINT DEFAULT NULL,
  L6Code TINYINT DEFAULT NULL,
  Percentile DOUBLE PRECISION,
  nSamples MEDIUMINT,
  MeanHandRank DOUBLE PRECISION,
  DateGenerated DATE,
  TimeAdded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX (PoolSize, SetSize)
)

-- Weights summed over all rows grouped on StrategyID should give 1.
-- Weights summed over all rows grouped on StrategyID and SetNo give the set weights
CREATE TABLE percentile_strategy_weights
(
  StrategyID SMALLINT NOT NULL,
  SetNo TINYINT NOT NULL,
  PoolSize TINYINT NOT NULL,
  SetSize TINYINT NOT NULL,
  CodeMaxLevel TINYINT NOT NULL,
  Weight DOUBLE PRECISION,
  TimeAdded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE INDEX (StrategyID, SetNo, PoolSize, SetSize),
  FOREIGN KEY (StrategyID)
    REFERENCES split_strategies(StrategyID)
    ON DELETE CASCADE
)


-- TODO

-- Add current strategy
-- StrategyID = 1, StrategyTypeID = 1
-- 3 of 5, 5 of 8, 5 of 11

-- (StrategyID, SetNo, PoolSize, SetSize, Weight)
-- (1, 1, 5, 3, 1/3)
-- (1, 2, 8, 5, 1/3)
-- (1, 3, 11, 5, 1/3)



INSERT INTO split_strategy_types (StrategyTypeID, Description) VALUES (1, 'WeightedPercentiles')