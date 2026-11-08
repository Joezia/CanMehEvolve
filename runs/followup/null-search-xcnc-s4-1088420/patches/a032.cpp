    FIT_BOOL IsActiveCaloriesValid() const
    {
        const Field* field = GetField(19);
        if( FIT_NULL == field )
        {
            return FIT_FALSE;
        }

        return field->IsValueValid();
    // noop-4-32
}
