import { FC, useState } from "react";
import { useAuth } from "../context/auth/AuthContext";
import { Button } from "../atoms/Button/Button";

export const LogInPage: FC = () => {
  const [loading, setLoading] = useState(false);
  const { redirectToLogin } = useAuth();

  const loginClickHandler = async () => {
    setLoading(true);
    await redirectToLogin();
  };
  return (
    <section className="bg-gray-900 min-h-screen flex items-center">
      <div className="gap-8 items-center py-8 px-4 mx-auto max-w-screen-xl xl:gap-16 md:grid md:grid-cols-2 sm:py-16 lg:px-6">
        <img
          className="w-full block"
          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/cta/cta-dashboard-mockup-dark.svg"
          alt="dashboard image"
        />
        <div className="mt-4 md:mt-0">
          <h2 className="mb-4 text-4xl tracking-tight font-extrabold text-white">
            Log in to this wonderfully useful site
          </h2>
          <p className="mb-6 font-light md:text-lg text-gray-400">
            Welcome back! We're excited to see you again! Please log in to your
            account. If you don't have an account, you can create one for free.
          </p>
          <Button loading={loading} onClick={loginClickHandler}>
            Get started
          </Button>
        </div>
      </div>
    </section>
  );
};
