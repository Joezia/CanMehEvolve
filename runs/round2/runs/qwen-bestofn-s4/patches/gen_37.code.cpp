
FIT_BOOL IsTimestampValid() const
{
    const Field* field = GetField(253);
    return (field && field->IsValueValid()) ? FIT_TRUE : FIT_FALSE;
}
