FieldBase::FieldBase(const FieldBase &field)
{
    if (!field.values.empty())
    {
        values = field.values;
    }
    if (!field.stringIndexes.empty())
    {
        stringIndexes = field.stringIndexes;
    }
}
