import { FC } from "react";
import { useGetMyListings } from "../hooks/useGetMyListings";
import { LoadingSkeleton } from "../atoms/LoadingSkeleton/LoadingSkeleton";
import { List, ListItem } from "../atoms/List/List";
import { Alert } from "../atoms/Alert/Alert";

export const MyListingsPage: FC = () => {
  const { listings, isLoading } = useGetMyListings({
    offset: 0,
    page_size: 10,
  });
  if (isLoading) {
    return <LoadingSkeleton />;
  }
  if (!listings || listings.length === 0) {
    return (
      <div>
        <h1 className="text-3xl font-extrabold text-white mb-4">My listings</h1>
        <Alert color="info" title="No listings yet">
          You haven’t created any listings. Once you add one, it’ll show up
          here.
        </Alert>
      </div>
    );
  }
  return (
    <div>
      <h1 className="text-3xl font-extrabold text-white mb-4">My listings</h1>
      <List className="w-full">
        {listings.map((listing) => (
          <ListItem key={listing.id} linkTo={`/listings/${listing.id}`}>
            {listing.title}
          </ListItem>
        ))}
      </List>
    </div>
  );
};
