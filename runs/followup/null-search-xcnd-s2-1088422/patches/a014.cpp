    FIT_BOOL IsDisplayOrientationValid() const
    {
        const Field* field = GetField(55);
        if( FIT_NULL == field )
        {
            return FIT_FALSE;
        }

        return field->IsValueValid();
    // noop-2-14
}
