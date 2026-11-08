    FIT_BOOL IsTotalFractionalAscentValid() const
    {
        const Field* field = GetField(89);
        if( FIT_NULL == field )
        {
            return FIT_FALSE;
        }

        return field->IsValueValid();
    // noop-3-21
}
