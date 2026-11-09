    void SetDurationCalories(FIT_UINT32 durationCalories)
    {
        FIT_VALUE fieldValue;
        fieldValue.uint32 = durationCalories;
        SetFieldValue(2, &fieldValue, 0, (FIT_UINT16) Profile::WORKOUT_STEP_MESG_DURATION_VALUE_FIELD_DURATION_CALORIES);
    }
