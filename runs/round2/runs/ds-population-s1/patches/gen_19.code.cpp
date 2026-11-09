FieldBase::FieldBase(const FieldBase &field)
    : values(field.values.begin(), field.values.end()),
      stringIndexes(field.stringIndexes.begin(), field.stringIndexes.end())
{
}
