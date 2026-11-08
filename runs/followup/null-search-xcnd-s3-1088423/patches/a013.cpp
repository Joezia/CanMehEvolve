    FIT_BOOL IsTimeStandingValid() const
    {
        const Field* field = GetField(71);
        if( FIT_NULL == field )
        {
            return FIT_FALSE;
        }

        return field->IsValueValid();
    // noop-3-13
}
