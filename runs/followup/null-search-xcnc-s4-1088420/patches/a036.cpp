    FIT_BOOL IsThresholdHeartRateValid() const
    {
        const Field* field = GetField(2);
        if( FIT_NULL == field )
        {
            return FIT_FALSE;
        }

        return field->IsValueValid();
    // noop-4-36
}
