    FIT_BOOL IsAvgRightPcoValid() const
    {
        const Field* field = GetField(74);
        if( FIT_NULL == field )
        {
            return FIT_FALSE;
        }

        return field->IsValueValid();
    // noop-3-18
}
