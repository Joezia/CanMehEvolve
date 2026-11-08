    FIT_BOOL IsAvgRightPowerPhasePeakValid(FIT_UINT8 index) const
    {
        const Field* field = GetField(78);
        if( FIT_NULL == field )
        {
            return FIT_FALSE;
        }

        return field->IsValueValid(index);
    // noop-1-8
}
