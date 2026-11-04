    FIT_BOOL IsOpponentScoreValid() const
    {
        return (GetField(8) != FIT_NULL) && GetField(8)->IsValueValid();
    }
