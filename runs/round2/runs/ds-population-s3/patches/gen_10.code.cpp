    FIT_FLOAT32 GetRepeatDistance(void) const
    {
        const FIT_UINT16 subfield = (FIT_UINT16) Profile::WORKOUT_STEP_MESG_TARGET_VALUE_FIELD_REPEAT_DISTANCE;
        return GetFieldFLOAT32Value(4, 0, subfield);
    }

